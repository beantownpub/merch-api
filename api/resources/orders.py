import json
import logging
import os
import psycopg2
import requests

from flask import Response, request, session
from flask_httpauth import HTTPBasicAuth
from flask_restful import Resource
from werkzeug.security import generate_password_hash, check_password_hash

from api.database.models import Address, Customer, Order, Product, Cart, CartItem, Inventory
from api.database.db import DB
from api.libs.db_utils import run_db_action, get_item_from_db
from api.libs.utils import make_uuid, ParamArgs
from api.libs.logging import init_logger
from api.libs.notify import send_order_confirmation

AUTH = HTTPBasicAuth()
LOG_LEVEL= os.environ.get('LOG_LEVEL')
LOG = init_logger(log_level=LOG_LEVEL)


class OrdersAPIException(Exception):
    """Base class for menu database exceptions"""


@AUTH.verify_password
def verify_password(username, password):
    api_pwd = os.environ.get("API_PASSWORD")
    if password.strip() == api_pwd:
        verified = True
    else:
        verified = False
    return verified


def clear_cart(cart_items, cart_id):
    for cart_item in cart_items:
        LOG.debug('Deleting Cart Item %s', cart_item['name'])
        sku = cart_item['sku']
        product = Product.objects(sku=int(sku)).first()
        item = CartItem.objects(item=product, cart_id=cart_id).first()
        cart = Cart.objects(cart_id=cart_id).first()
        cart.cart_items.remove(item)
        cart.save()
        item.delete()


def get_customer(email_address):
    customer = get_item_from_db('customers', query={"email_address": email_address})
    LOG.debug(' - OrdersAPI | get_customer | %s', customer)
    return customer


def get_order(cart_id):
    order = get_item_from_db('orders', query={"cart_id": cart_id})
    LOG.debug(' - OrdersAPI | get_order | %s', order)
    return order


def get_all_orders():
    orders = Order.query.filter_by().all()
    return orders

def create_address(data):
    LOG.debug('Creating address: %s', data)
    address = Address(
        street=data['street'],
        unit=data['unit'],
        city=data['city'],
        state=data['state'],
        zip_code=data['zipCode']
    )
    DB.session.add(address)
    DB.session.commit()
    return address


def create_customer(data):
    email = data['email']
    if not get_customer(email):
        LOG.debug('Creating customer: %s', email)
        address = create_address(data)
        LOG.debug('Customer address: %s', address)
        customer = Customer(
            first_name=data['firstName'],
            last_name=data['lastName'],
            # phone_number=data['phone_number'],
            email_address=email,
            address=address.id
        )
        DB.session.add(customer)
        DB.session.commit()
    customer = get_customer(data['email'])
    if customer:
        return customer


def create_order(data, customer, location=None):
    LOG.debug('Creating order from cart %s', data['cart_id'])
    LOG.debug('Creating order for %s', customer.id)
    # cart = get_item_from_db('cart', query={"cart_id": data['cart_id']})
    order = Order(
        customer=customer.email_address,
        cart_id=data['cart_id'],
        items=data['cart_items'],
        uuid=make_uuid(),
        location=location
    )
    DB.session.add(order)
    DB.session.commit()
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
    LOG.debug('- Adding to order: Name: %s | Data: %s', product.name, item)
    run_db_action(action='create', data=item, table='order_item', query={"cart_id": cart.cart_id})

def _upadte_inventory_size_quantity(inventory, size, quantity):
    sizes = {
        "small": inventory.small,
        "medium": inventory.medium,
        "large": inventory.large,
        "xl": inventory.xl,
        "xxl": inventory.xxl
    }
    inventory = sizes.get(size)

class OrdersAPI(Resource):
    # @auth.login_required
    def get(self):
        orders = get_all_orders()
        LOG.debug('OrdersAPI | GET | %s', orders)
        order_list = []
        for order in orders:
            LOG.debug('Order | Customer | %s', order.customer)
            LOG.debug('Order | Items | %s', order.order_items)
            order_data = {
                "id": order.id,
            }
            order_list.append(order_data)
        return Response(json.dumps(order_list), mimetype='application/json', status=200)

    @AUTH.login_required
    def post(self):
        args = ParamArgs(request.args)
        data = request.get_json()
        LOG.info('| OrderAPI | POST | Location: %s | DATA: %s',args.location, data['order'])
        order = self._create_order(data, args.location)
        order_data = {
            'order_id': order.id
        }
        order_data = json.dumps(order_data)
        confirmation_status = send_order_confirmation(data)
        if confirmation_status.status_code != 200:
            resp = {"status": 500, "response": f"Error confirming order"}
        else:
            resp = {"status": 200, "response": order_data, "mimetype": "application/json"}
        return Response(**resp)

    @AUTH.login_required
    def delete(self):
        sku = request.get_json()['sku']
        Order.objects.get(sku=sku).delete()
        return '', 204

    def _create_order(self, data, location=None):
        customer_info = data['order']
        order_info = customer_info['cart']
        self._update_inventory(order_info['cart_items'])
        customer = create_customer(customer_info)
        order = create_order(order_info, customer, location=location)
        return order

    def _update_inventory(self, cart_items):
        for item in cart_items:
            product = Product.query.filter_by(id=item['sku']).first()
            inventory = Inventory.query.filter_by(id=product.id).first()
            if not product.has_sizes:
                new_quantity = inventory.quantity - item['quantity']
                inventory.quantity = new_quantity
            else:
                if item['size'] == 'small':
                    new_quantity = inventory.small - item['quantity']
                    inventory.small = new_quantity
                elif item['size'] == 'medium':
                    new_quantity = inventory.medium - item['quantity']
                    inventory.medium = new_quantity
                elif item['size'] == 'large':
                    new_quantity = inventory.large - item['quantity']
                    inventory.large = new_quantity
                elif item['size'] == 'xl':
                    new_quantity = inventory.xl - item['quantity']
                    inventory.xl = new_quantity
                elif item['size'] == 'xxl':
                    new_quantity = inventory.xxl - item['quantity']
                    inventory.xxl = new_quantity
            DB.session.add(inventory)
            DB.session.commit()




class OrderAPI(Resource):
    def get(self, order_id):
        # order_id = session.get('CART_ID')
        LOG.debug('OrderAPI | GET | ORDER ID: %s', order_id)
        cart = get_item_from_db('cart', {"cart_id": order_id})

        cart_items = self._get_cart_items(order_id)
        for item in cart_items:
            logging.info('OrdersAPI | Item: %s', item)
            logging.info('OrdersAPI | Item dir: %s', dir(item))
        order_data = {
            'order_items': 'foo'
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
        LOG.debug('OrderAPI | _get_cart_items | cart_id: %s', cart_id)
        cart = get_item_from_db('cart', query={"cart_id": cart_id})
        LOG.debug('Cart Items debug: %s', cart.items)
        query = {"cart_id": cart.cart_id}
        cart_items = get_item_from_db('cart_item', query=query, multiple=True)
        return cart_items
