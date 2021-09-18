import json
import logging
import random
from flask import Response, request, session
from flask_restful import Resource

from api.database.mongo_models import Cart, CartItem, Product, Customer

app_log = logging.getLogger()


if __name__ != '__main__':
    gunicorn_logger = logging.getLogger('gunicorn.error')
    app_log.handlers = gunicorn_logger.handlers
    app_log.setLevel('INFO')


def _generate_cart_id():
    """Generate and return a random cart_id"""
    cart_id = ''
    characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890!@#$%^&*'
    cart_id_length = 25
    for _ in range(cart_id_length):
        cart_id += characters[random.randint(0, len(characters) - 1)]
    app_log.info('- Generated Cart ID: %s', cart_id)
    return cart_id


class CartAPI(Resource):
    def get(self):
        app_log.info('SESSION: %s', session.keys())
        cart_id = session.get('CART_ID')
        if not cart_id:
            # app_log.info('- CartAPI | GET | cart_id not found')
            cart = self.create_cart()
            cart_id = cart.cart_id
            # app_log.info('- NEW CART: %s', cart)
            # app_log.info('- CartAPI | GET | New Cart ID: %s', cart_id)
        else:
            cart = self.get_cart(cart_id).to_json()
            # app_log.info('- CartAPI | GET | Cart ID %s', cart_id)
        cart_info = self.get_cart_items(cart_id)
        # app_log.info('- CartAPI | GET | Cart INFO: %s', cart_info)
        return Response(json.dumps(cart_info), mimetype='application/json', status=200)

    def post(self):
        app_log.info('- CartAPI | POST')
        cart_id = session.get('CART_ID')
        cart = Cart.objects(cart_id=cart_id).first()
        body = request.get_json()
        sku = body['sku']
        quantity = body['quantity']
        size = body['size']
        product = Product.objects(sku=sku).first()
        cart_item = CartItem(item=product, cart_id=cart_id, item_count=quantity, size=size)
        cart_item = cart_item.save()
        cart.cart_items.append(cart_item)
        cart.save()
        cart_info = self.get_cart_items(cart_id)
        # app_log.info('- CartAPI | POST | Cart INFO: %s', cart_info)
        return Response(json.dumps(cart_info), mimetype='application/json', status=200)

    def delete(self):
        app_log.info('- CartAPI | DELETE')
        cart_id = session.get('CART_ID')
        sku = request.get_json()['sku']
        product = Product.objects(sku=int(sku)).first()
        cart_item = CartItem.objects(item=product, cart_id=cart_id).first()
        cart = Cart.objects(cart_id=cart_id).first()
        try:
            cart.cart_items.remove(cart_item)
            cart.save()
            cart_item.delete()
        except ValueError:
            app_log.error('WTF')
            Cart.objects(cart_id=cart_id).delete()
            cart = self.create_cart()
        cart_info = self.get_cart_items(cart_id)
        # app_log.info('- CartAPI | DELETE | Cart INFO: %s', cart_info)
        return Response(json.dumps(cart_info), mimetype='application/json', status=200)

    def create_cart(self, cart_id=None):
        app_log.info('- CartAPI | create_cart')
        if not cart_id:
            cart_id = _generate_cart_id()
            session['CART_ID'] = cart_id
        cart = Cart(cart_id=cart_id).save()
        return cart

    def get_cart(self, cart_id):
        app_log.info(' - CartAPI | get_cart')
        cart = Cart.objects(cart_id=cart_id).first()
        if not cart:
            cart = self.create_cart(cart_id=cart_id)
        return cart

    def get_cart_items(self, cart_id):
        app_log.info(' - CartAPI | get_cart_items')
        cart_data = {
            'cart_items': [],
            'cart_id': cart_id
        }
        cart = Cart.objects(cart_id=cart_id).first()
        if not cart:
            cart = self.create_cart(cart_id=cart_id)
        for item in cart.cart_items:
            item_info = {}
            item_info['quantity'] = item.item_count
            item_info['sku'] = item.item.sku
            item_info['name'] = item.item.name
            item_info['price'] = item.item.price
            item_info['sizes'] = item.item.sizes
            if item.size:
                item_info['size'] = item.size
            else:
                item_info['size'] = False
            item_info['total'] = item_info['quantity'] * item_info['price']
            cart_data['cart_items'].append(item_info)
        cart_data['total'] = self.calculate_cart_total(cart_id)
        return cart_data

    def calculate_cart_total(self, cart_id):
        item_prices = []
        cart = Cart.objects(cart_id=cart_id).first()
        for cart_item in cart.cart_items:
            item_count = cart_item.item_count
            price = cart_item.item.price
            item_prices.append(item_count * price)
        return round(sum(item_prices), 2)


class CheckoutAPI(Resource):
    def post(self):
        app_log.info('- CheckoutAPI | POST')
        cart_id = session.get('CART_ID')
        cart = Cart.objects(cart_id=cart_id).first()
        body = request.get_json()
        app_log.info('- CheckoutAPI | Body: %s', body)
        sku = body['sku']
        quantity = body['quantity']
        size = body['size']
        product = Product.objects(sku=sku).first()
        customer = Customer(item=product, cart_id=cart_id, item_count=quantity, size=size)
        customer.save()
        cart.save()
        cart_info = self.get_cart_items(cart_id)
        app_log.info('- CartAPI | POST | Cart INFO: %s', cart_info)
        return Response(json.dumps(cart_info), mimetype='application/json', status=200)
