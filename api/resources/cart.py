import json
import os
from flask import Response, request, session
from flask_httpauth import HTTPBasicAuth
from flask_restful import Resource

from api.libs.logging import init_logger
from api.libs.db_utils import run_db_action, get_item_from_db
from api.libs.utils import cart_item_to_dict, ParamArgs

AUTH = HTTPBasicAuth()
LOG_LEVEL= os.environ.get('LOG_LEVEL')
LOG = init_logger(log_level=LOG_LEVEL)


@AUTH.verify_password
def verify_password(username, password):
    LOG.info('Verifying user | %s', username)
    api_pwd = os.environ.get("API_PASSWORD")
    if password.strip() == api_pwd:
        verified = True
    else:
        LOG.info('Access Denied - %s', username)
        verified = False
    return verified


def add_to_cart(product, data, cart):
    LOG.info('Adding to cart | %s | %s', product, data)
    item = {
        "product_id": product.name,
        "item_count": data['quantity'],
        "cart_id": cart.cart_id
    }
    category = get_item_from_db('category', query={"name": product.category_id})
    LOG.info('Cart product category | %s', category.name)
    LOG.info('Category sizes | %s', category.has_sizes)
    if category.has_sizes:
        item["size"] = data["size"]
    query = {"product": product, "cart_id": cart.cart_id}
    cart_item = get_item_from_db('cart_item', query=query, multiple=False)
    if cart_item:
        if category.has_sizes:
            if cart_item.size == data["size"]:
                delete_from_cart(product, cart.cart_id)
    LOG.info('Adding %s to cart | Data: %s', product.name, item)
    run_db_action(action='create', data=item, table='cart_item', query={"cart_id": cart.cart_id})
    cart_item = get_item_from_db('cart_item', query=query, multiple=False)
    LOG.info('CART Items | %s', cart.items)


def delete_from_cart(product, cart_id):
    cart = get_item_from_db('cart', query={"cart_id": cart_id})
    query = {"product": product, "cart_id": cart_id}
    cart_item = get_item_from_db('cart_item', query=query)
    run_db_action(action='delete', item=cart_item, table='cart_item', query={"cart_id": cart_id, "cart": cart})


def _get_cart_items(cart_id):
    LOG.debug('cart_id: %s', cart_id)
    cart_data = {
        'cart_items': [],
        'cart_id': cart_id
    }
    cart = get_item_from_db('cart', query={"cart_id": cart_id})
    LOG.info('Cart items debug | %s | %s', cart, cart.items)
    for item in cart.items:
        if item.product:
            item_data = cart_item_to_dict(item)
            LOG.info('Cart item: %s', item_data)
            cart_data['cart_items'].append(item_data)
        else:
            LOG.debug('Item not present: %s', item)
    cart_data['total'] = _calculate_cart_total(cart)
    LOG.debug('Cart Data: %s', cart_data)
    return cart_data


def _calculate_cart_total(cart):
        item_prices = []
        # LOG.info('Getting cart items from db  - Query: %s', query)
        cart_items = get_item_from_db('cart_item', query={"cart_id": cart.cart_id}, multiple=True)
        for item in cart_items:
            if item.product:
                item_count = item.item_count
                price = item.product.price
                item_prices.append(item_count * price)
            else:
                LOG.error('Item not present | %s', item)
        return round(sum(item_prices), 2)


class CartAPI(Resource):
    @AUTH.login_required
    def get(self):
        LOG.debug('Session Items: %s', session.items())
        # LOG.info('Headers: %s', request.headers)
        LOG.info('CartAPI | GET Cart-Id | %s', request.headers.get('Cart-Id'))
        cart_id = request.headers.get('Cart-Id')
        if not cart_id:
            LOG.error('Cart-Id header not found')
            resp = {"status": 400, "response": "Cart-Id not found"}
        else:
            cart = self._create_cart(cart_id=request.headers.get('Cart-Id'))
            if not cart:
                LOG.error('CartAPI | Cart ID missing from DB | %s', cart_id)
                cart = self._create_cart(cart_id=cart_id)
            cart_info = _get_cart_items(cart.cart_id)
            LOG.debug('CartAPI | GET | Cart INFO: %s', cart_info)
            resp = {"status": 200, "response": json.dumps(cart_info), "mimetype": "application/json"}
        return Response(**resp)

    @AUTH.login_required
    def post(self):
        cart_id = request.headers.get('Cart-Id')
        if not cart_id:
            LOG.error('Cart-Id header not found')
            resp = {"status": 400, "response": "Cart-Id not found"}
        else:
            data = request.get_json()
            LOG.info('ADDING TO CART | %s | data | %s', cart_id, data)
            product = get_item_from_db('product', query={"id": data['sku']})
            LOG.info('ADDING TO CART | product | %s', product)
            LOG.info(dir(product))
            category = get_item_from_db('category', query={"name": product.category_id})
            LOG.info('Category | %s', category.name)
            cart = get_item_from_db('cart', {"cart_id": cart_id})
            add_to_cart(product, data, cart)
            cart_info = _get_cart_items(cart.cart_id)
            LOG.debug('POST | Cart data: %s', cart_info)
            resp = {"status": 200, "response": json.dumps(cart_info), "mimetype": "application/json"}
        return Response(**resp)

    @AUTH.login_required
    def delete(self):
        """Delete an item from the cart"""
        cart_id = session.get('CART_ID')
        if not cart_id:
            cart_id = request.headers.get('Cart-Id')
        LOG.info('CartAPI | DELETE Cart ID | %s', cart_id)
        sku = request.get_json()['sku']
        product = get_item_from_db('product', query={"id": sku})
        query = {"product": product, "cart_id": cart_id}
        cart_item = get_item_from_db('cart_item', query=query)
        run_db_action(action='delete', item=cart_item, table='cart_item', query={"cart_id": cart_id})
        cart_info = _get_cart_items(cart_id)
        return Response(json.dumps(cart_info), mimetype='application/json', status=200)

    def _create_cart(self, cart_id):
        session['CART_ID'] = cart_id
        data = {"cart_id": cart_id}
        cart = get_item_from_db('cart', query={"cart_id": cart_id})
        if not cart:
            LOG.info('CartAPI | Adding Cart ID to DB | %s', cart_id)
            run_db_action(action='create', data=data, table='cart', query={"cart_id": cart_id})
            cart = get_item_from_db('cart', query={"cart_id": cart_id})
        else:
            LOG.info('CartAPI | Cart ID already exists | %s', cart_id)
        return cart

    def _get_cart(self, cart_id):
        LOG.debug('CartAPI | _get_cart | %s', cart_id)
        cart = get_item_from_db('cart', query={"cart_id": cart_id})
        if not cart:
            cart = self._create_cart(cart_id=cart_id)
        return cart


class CheckoutAPI(Resource):
    @AUTH.login_required
    def post(self):
        pass

    @AUTH.login_required
    def get(self):
        args = ParamArgs(request.args)
        query = {"cart_id": args.cart_id}
        cart_list = []
        cart_items = get_item_from_db('cart_item', query=query, multiple=True)
        for item in cart_items:
            if item.product:
                LOG.info('item: %s', item.product.name)
                item_data = cart_item_to_dict(item)
                cart_list.append(item_data)
            else:
                LOG.debug('Item not present: %s', item)
        return Response(json.dumps(cart_list), mimetype='application/json', status=200)

    @AUTH.login_required
    def delete(self):
        args = ParamArgs(request.args)
        LOG.info('Clearing cart %s', args)
        query = {"cart_id": args.cart_id}
        cart_items = get_item_from_db('cart_item', query=query, multiple=True)
        for item in cart_items:
            if item.product:
                LOG.info('deleting item: %s', item.product.name)
                run_db_action(action='delete', item=item, table='cart_item', query={"cart_id": args.cart_id})
            else:
                LOG.debug('Item not present: %s', item)
        cart = _get_cart_items(args.cart_id)
        return Response(json.dumps(cart), mimetype='application/json', status=200)
