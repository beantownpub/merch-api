import json
import logging
import os
import psycopg2
import requests

from flask import Response, request, session
from flask_httpauth import HTTPBasicAuth
from flask_restful import Resource
from werkzeug.security import generate_password_hash, check_password_hash

from api.database.models import Order, Product, Cart, CartItem

app_log = logging.getLogger()

SECRET_KEY = 'go-fuck-yourself'

auth = HTTPBasicAuth()

if __name__ != '__main__':
    gunicorn_logger = logging.getLogger('gunicorn.error')
    app_log.handlers = gunicorn_logger.handlers
    app_log.setLevel('INFO')


def connect_to_db():
    db = os.environ.get("AUTH_DB")
    db_user = os.environ.get("AUTH_DB_USER")
    db_pw = os.environ.get("AUTH_DB_PW")
    # db_host = os.environ.get("AUTH_DB_HOST", "172.17.0.6")
    db_host = 'localhost'
    db_port = os.environ.get("AUTH_DB_PORT", "5432")
    conn = psycopg2.connect(
        database=db,
        user=db_user,
        password=db_pw,
        host=db_host,
        port=db_port
    )
    return conn


@auth.verify_password
def verfify_password(username, password):
    account = get_account(username)
    if account:
        _id, user, password_hash = account
        if check_password_hash(password_hash, password):
            return True
    return False


def get_account(user):
    conn = connect_to_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM accounts WHERE username=%s", (user,))
    account = cur.fetchone()
    conn.close()
    if account:
        _id, user, password = account
        return _id, user, generate_password_hash(password)


def sendNotifications(data):
    url = 'http://172.17.0.5:5012/v1/contact/merch'
    headers = {'Content-Type': 'application/json'}
    req = requests.post(url, headers=headers, json=data)
    logging.info('Contact Request: %s', req.status_code)


def _cart(cart):
    app_log.info('CI 1: %s', cart.cart_items)
    app_log.info('LEN: %s', len(cart.cart_items))
    for cart_item in cart.cart_items:
        app_log.info('cart item: %s', cart_item.item.name)
        cart.cart_items.remove(cart_item)
        cart.save()
    cart.save()
    app_log.info('CI 2: %s', cart.cart_items)


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


class OrdersAPI(Resource):
    @auth.login_required
    def get(self):
        orders = Order.objects().to_json()
        return Response(orders, mimetype='application/json', status=200)

    @auth.login_required
    def post(self):
        body = request.get_json()
        app_log.info(body)
        app_log.info(request.authorization)
        cart_id = body['order']['cart']['cart_id']
        logging.info('Deleting cart %s', cart_id)
        # cart_items = body['order']['cart']['cart_items']
        # sendNotifications(body)
        Cart.objects.get(cart_id=cart_id).delete()
        # clear_cart(cart_items, cart_id)
        # product = Order(**body).save()
        # _id = product.id
        cart_data = {
            'cart_items': [],
            'cart_id': cart_id
        }
        return Response(json.dumps(cart_data), mimetype='application/json', status=200)

    def delete(self):
        sku = request.get_json()['sku']
        Order.objects.get(sku=sku).delete()
        return '', 204


class OrderAPI(Resource):
    def get(self, _id):
        product = Order.objects.get(id=_id).to_json()
        return Response(product, mimetype="application/json", status=200)

    def put(self, _id):
        body = request.get_json()
        Order.objects.get(id=_id).update(**body)
        return '', 200

    def delete(self, sku):
        Order.objects.get(sku=sku).delete()
        return '', 200
