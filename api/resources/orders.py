import json
import logging
import os
import psycopg2
import requests

from flask import Response, request, session
from flask_httpauth import HTTPBasicAuth
from flask_restful import Resource
from werkzeug.security import generate_password_hash, check_password_hash

from api.database.models import Address, Customer, Order, Product, Cart, CartItem
from api.database.db import db
from api.libs.db_utils import run_db_action, get_item_from_db
from api.libs.utils import cart_item_to_dict, get_cart_items

app_log = logging.getLogger()

auth = HTTPBasicAuth()

class OrdersAPIException(Exception):
    """Base class for menu database exceptions"""

if __name__ != '__main__':
    gunicorn_logger = logging.getLogger('gunicorn.error')
    app_log.handlers = gunicorn_logger.handlers
    log_level = os.environ.get('LOG_LEVEL', 'INFO')
    app_log.setLevel(log_level)


@auth.verify_password
def verfify_password(username, password):
    account = get_account(username)
    if account:
        _id, user, password_hash = account
        if check_password_hash(password_hash, password):
            return True
    return False


def clear_cart(cart_items, cart_id):
    for cart_item in cart_items:
        app_log.info('Deleting Cart Item %s', cart_item['name'])
        sku = cart_item['sku']
        product = Product.objects(sku=int(sku)).first()
        item = CartItem.objects(item=product, cart_id=cart_id).first()
        cart = Cart.objects(cart_id=cart_id).first()
        cart.cart_items.remove(item)
        cart.save()
        item.delete()


def get_customer(email_address):
    customer = get_item_from_db('customers', query={"email_address": email_address})
    app_log.debug(' - OrdersAPI | get_customer | %s', customer)
    return customer


def get_order(cart_id):
    order = get_item_from_db('orders', query={"cart_id": cart_id})
    app_log.debug(' - OrdersAPI | get_order | %s', order)
    return order


def get_all_orders():
    orders = Order.query.filter_by().all()
    return orders

def create_address(data):
    app_log.debug('Creating address: %s', data)
    address = Address(
        street=data['street'],
        unit=data['unit'],
        city=data['city'],
        state=data['state'],
        zip_code=data['zipCode']
    )
    db.session.add(address)
    db.session.commit()
    return address


def create_customer(data):
    email = data['email']
    if not get_customer(email):
        app_log.debug('Creating customer: %s', email)
        address = create_address(data)
        app_log.debug('Customer address: %s', address)
        customer = Customer(
            first_name=data['firstName'],
            last_name=data['lastName'],
            # phone_number=data['phone_number'],
            email_address=email,
            address=address.id
        )
        db.session.add(customer)
        db.session.commit()
    customer = get_customer(data['email'])
    if customer:
        return customer


def create_order(data, customer):
    app_log.debug('Creating order from cart %s', data['cart_id'])
    app_log.debug('Creating order for %s', customer.id)
    # cart = get_item_from_db('cart', query={"cart_id": data['cart_id']})
    order = Order(
        customer=customer.email_address,
        cart_id=data['cart_id'],
        items=data['cart_items']
    )
    db.session.add(order)
    db.session.commit()
    return order


def delete_from_order(product, cart_id):
    cart = get_item_from_db('cart', query={"cart_id": cart_id})
    query = {"product": product, "cart_id": cart_id}
    order_item = get_item_from_db('order_item', query=query)
    run_db_action(action='delete', item=order_item, table='order_item', query={"cart_id": cart_id, "cart": cart})


def add_to_order(product, data, cart):
    item = {
        "product": product,
        "item_count": data['quantity'],
        "cart": cart,
        "cart_id": cart.cart_id
    }
    # query = {"product": product, "cart_id": cart.cart_id}
    query = {"product": product, "cart_id": cart.cart_id}
    order_item = get_item_from_db('order_item', query=query, multiple=False)
    if order_item:
        delete_from_order(product, cart.cart_id)
    app_log.debug('- Adding to order: Name: %s | Data: %s', product.name, item)
    run_db_action(action='create', data=item, table='order_item', query={"cart_id": cart.cart_id})


class OrdersAPI(Resource):
    # @auth.login_required
    def get(self):
        orders = get_all_orders()
        app_log.debug('OrdersAPI | GET | %s', orders)
        order_list = []
        for order in orders:
            app_log.debug('Order | Customer | %s', order.customer)
            app_log.debug('Order | Items | %s', order.order_items)
            order_data = {
                "id": order.id,
            }
            order_list.append(order_data)
        return Response(json.dumps(order_list), mimetype='application/json', status=200)

    # @auth.login_required
    def post(self):
        data = request.get_json()
        app_log.info('| OrderAPI | POST | DATA: %s', data['order'])
        order = self._create_order(data)
        order_data = {
            'order_id': order.id
        }
        return Response(json.dumps(order_data), mimetype='application/json', status=200)

    def delete(self):
        sku = request.get_json()['sku']
        Order.objects.get(sku=sku).delete()
        return '', 204

    def _create_order(self, data):
        customer_info = data['order']
        order_info = customer_info['cart']
        customer = create_customer(customer_info)
        order = create_order(order_info, customer)
        return order



class OrderAPI(Resource):
    def get(self, order_id):
        # order_id = session.get('CART_ID')
        app_log.debug('OrderAPI | GET | ORDER ID: %s', order_id)
        cart = get_item_from_db('cart', {"cart_id": order_id})

        cart_items = self._get_cart_items(order_id)
        for item in cart_items:
            logging.info('OrdersAPI | Item: %s', item)
            logging.info('OrdersAPI | Item dir: %s', dir(item))
        order_data = {
            'order_items': 'foo'
        }
        return Response(json.dumps(order_data), mimetype='application/json', status=200)

    def post(self, order):
        order_id = session.get('CART_ID')
        app_log.debug('- OrderAPI | POST | Session ORDER ID: %s', order_id)
        cart = get_item_from_db('cart', {"cart_id": order_id})
        if not cart:
            raise OrdersAPIException(f"Cannot complete order. Cart {order_id} not found.")
        cart_items = self._get_cart_items(order_id)
        for item in cart.items:
            logging.info('OrdersAPI | Cart item: %s', item)
            logging.info('OrdersAPI | Cart item dir: %s', dir(item))
        add_to_order(product, data, cart)
        data = request.get_json()
        logging.info('Order data: %s', data)
        customer = create_customer(data)
        order = create_order(data, customer)
        logging.info('Order created: %s', order)
        order_data = {
            'order_items': order.order_items,
            'order_id': order.id
        }
        return Response(json.dumps(order_data), mimetype='application/json', status=200)

    def put(self, _id):
        body = request.get_json()
        Order.objects.get(id=_id).update(**body)
        return '', 200

    def delete(self, sku):
        Order.objects.get(sku=sku).delete()
        return '', 200

    def _get_cart_items(self, cart_id):
        app_log.debug('OrderAPI | _get_cart_items | cart_id: %s', cart_id)
        cart = get_item_from_db('cart', query={"cart_id": cart_id})
        app_log.info('Cart Items debug: %s', cart.items)
        query = {"cart_id": cart.cart_id}
        cart_items = get_item_from_db('cart_item', query=query, multiple=True)
        return cart_items
