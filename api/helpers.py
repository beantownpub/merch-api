import json
from pymongo import MongoClient
from mongoengine import connection
from database.db import get_mongo_host
from database.models import Product, Inventory


MONGO_HOST = get_mongo_host()
CLIENT = MongoClient(MONGO_HOST)

connection.connect()


def log_request(func):
    def _request(*args, **kwargs):
        if kwargs.get('request'):
            request = kwargs['request']
            session = kwargs['session']
            app = kwargs.get('app')
            app.logger.debug(f"URL: {request.url}")
            app.logger.debug(f"SID: {session.sid}")
        response = func(*args, **kwargs)
        return response
    return _request


def _upload_products():
    """Upload products from products.json to DB"""
    with open('products.json') as f:
        products = json.load(f)
    for _, v in products['categories'].items():
        for i in v:
            inv = Inventory().save()
            product = Product(
                name=i['name'],
                quantity=inv,
                sku=i['sku'],
                price=i['price'],
                description=i['description'],
                category=i['category'],
                img_path=i['img_path']
            )
            print(product.name)
            product.save()


def _delete_products():
    for i in Product.objects():
        print(i.name)
        i.delete()


def _check_products():
    for i in Product.objects():
        print(i.name)


def _delete_sessions():
    db = CLIENT['merch']['cart_sessions']
    db.delete_many({})


def _delete_carts():
    db = CLIENT['merch']['shopping_cart']
    db.delete_many({})


def _delete_cart_items():
    db = CLIENT['merch']['cart_item']
    db.delete_many({})


def delete_data():
    _delete_cart_items()
    _delete_carts()
    _delete_sessions()


def reload_products():
    _delete_products()
    _upload_products()


def get_sessions():
    client = MongoClient(host=MONGO_HOST)
    db = client.merch
    sessions = db['cart-sessions']
    return sessions


if __name__ == '__main__':
    reload_products()

