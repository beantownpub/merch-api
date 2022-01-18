import json
import logging
import os
from flask import Response, request, session
from flask_restful import Resource

from api.libs.db_utils import run_db_action, get_item_from_db
from api.libs.utils import cart_item_to_dict, generate_cart_id, ParamArgs

app_log = logging.getLogger()


if __name__ != '__main__':
    gunicorn_logger = logging.getLogger('gunicorn.error')
    app_log.handlers = gunicorn_logger.handlers
    log_level = os.environ.get('LOG_LEVEL', 'INFO')
    app_log.setLevel(log_level)


def add_to_cart(product, data, cart):
    item = {
        "product_id": product.name,
        "item_count": data['quantity'],
        "cart": cart,
        "cart_id": cart.cart_id
    }
    # query = {"product": product, "cart_id": cart.cart_id}
    query = {"product": product, "cart_id": cart.cart_id}
    cart_item = get_item_from_db('cart_item', query=query, multiple=False)
    if cart_item:
        delete_from_cart(product, cart.cart_id)
    app_log.debug('- Adding to cart: Name: %s | Data: %s', product.name, item)
    run_db_action(action='create', data=item, table='cart_item', query={"cart_id": cart.cart_id})


def delete_from_cart(product, cart_id):
    cart = get_item_from_db('cart', query={"cart_id": cart_id})
    query = {"product": product, "cart_id": cart_id}
    cart_item = get_item_from_db('cart_item', query=query)
    run_db_action(action='delete', item=cart_item, table='cart_item', query={"cart_id": cart_id, "cart": cart})


def _get_cart_items(cart_id):
    app_log.debug(' - CartAPI | get_cart_items | cart_id: %s', cart_id)
    cart_data = {
        'cart_items': [],
        'cart_id': cart_id
    }
    cart = get_item_from_db('cart', query={"cart_id": cart_id})
    app_log.info('Cart Items debug: %s', cart.items)
    query = {"cart_id": cart.cart_id}
    # app_log.info('Getting cart items from db  - Query: %s', query)
    cart_items = get_item_from_db('cart_item', query=query, multiple=True)
    app_log.info('Items in cart: %s', cart_items)
    for item in cart_items:
        if item.product:
            app_log.info('item: %s', item.product.name)
            # app_log.debug('Item: %s', item.product.name)
            item_data = cart_item_to_dict(item)
            cart_data['cart_items'].append(item_data)
        else:
            app_log.debug('Item not present: %s', item)
    cart_data['total'] = _calculate_cart_total(cart)
    app_log.info('Cart Data: %s', cart_data)
    return cart_data


def _calculate_cart_total(cart):
        item_prices = []
        # app_log.info('Getting cart items from db  - Query: %s', query)
        cart_items = get_item_from_db('cart_item', query={"cart_id": cart.cart_id}, multiple=True)
        # cart_items = get_item_from_db('cart_item', query={"cart_id": cart_id}, multiple=True)
        for item in cart_items:
            if item.product:
                item_count = item.item_count
                price = item.product.price
                item_prices.append(item_count * price)
            else:
                app_log.debug('Item not present: %s', dir(item))
        return round(sum(item_prices), 2)

class CartAPI(Resource):
    def get(self):
        app_log.debug('Session Items: %s', session.items())
        cart_id = session.get('CART_ID')
        if not cart_id:
            app_log.debug('- CartAPI | GET | cart_id not found')
            cart = self._create_cart()
        else:
            app_log.debug('- CartAPI | GET | SESSION cart_id Found')
            cart = get_item_from_db('cart', {"cart_id": cart_id})
            if not cart:
                app_log.debug('- CartAPI | Cart missing from DB')
                cart = self._create_cart(cart_id=cart_id)
        cart_info = _get_cart_items(cart.cart_id)
        app_log.info('- CartAPI | GET | Cart INFO: %s', cart_info)
        return Response(json.dumps(cart_info), mimetype='application/json', status=200)

    def post(self):
        cart_id = session.get('CART_ID')
        app_log.debug('- CartAPI | POST | Session Cart ID: %s', cart_id)
        data = request.get_json()
        product = get_item_from_db('product', query={"id": data['sku']})
        cart = get_item_from_db('cart', {"cart_id": cart_id})
        add_to_cart(product, data, cart)
        cart_info = _get_cart_items(cart.cart_id)
        app_log.info('- CartAPI | POST | Cart INFO: %s', cart_info)
        return Response(json.dumps(cart_info), mimetype='application/json', status=200)

    def delete(self):
        """Delete an item from the cart"""
        app_log.debug('- CartAPI | DELETE')
        cart_id = session.get('CART_ID')
        sku = request.get_json()['sku']
        product = get_item_from_db('product', query={"id": sku})
        query = {"product": product, "cart_id": cart_id}
        cart_item = get_item_from_db('cart_item', query=query)
        run_db_action(action='delete', item=cart_item, table='cart_item', query={"cart_id": cart_id})
        cart_info = _get_cart_items(cart_id)
        return Response(json.dumps(cart_info), mimetype='application/json', status=200)

    def _create_cart(self, cart_id=None):
        app_log.debug('- CartAPI | create_cart | cart_id: %s', cart_id)
        if not cart_id:
            cart_id = generate_cart_id()
        session['CART_ID'] = cart_id
        data = {"cart_id": cart_id}
        run_db_action(action='create', data=data, table='cart', query={"cart_id": cart_id})
        cart = get_item_from_db('cart', query={"cart_id": cart_id})
        return cart

    def _get_cart(self, cart_id):
        app_log.debug(' - CartAPI | get_cart')
        cart = get_item_from_db('cart', query={"cart_id": cart_id})
        if not cart:
            cart = self._create_cart(cart_id=cart_id)
        return cart


class CheckoutAPI(Resource):
    def post(self):
        pass

    def get(self):
        args = ParamArgs(request.args)
        query = {"cart_id": args.cart_id}
        cart_list = []
        cart_items = get_item_from_db('cart_item', query=query, multiple=True)
        for item in cart_items:
            if item.product:
                app_log.info('item: %s', item.product.name)
                item_data = cart_item_to_dict(item)
                cart_list.append(item_data)
            else:
                app_log.debug('Item not present: %s', item)
        return Response(json.dumps(cart_list), mimetype='application/json', status=200)

    def delete(self):
        args = ParamArgs(request.args)
        query = {"cart_id": args.cart_id}
        cart_items = get_item_from_db('cart_item', query=query, multiple=True)
        for item in cart_items:
            if item.product:
                app_log.info('deleting item: %s', item.product.name)
                run_db_action(action='delete', item=item, table='cart_item', query={"cart_id": args.cart_id})
            else:
                app_log.debug('Item not present: %s', item)
        cart = _get_cart_items(args.cart_id)
        return Response(json.dumps(cart), mimetype='application/json', status=200)
