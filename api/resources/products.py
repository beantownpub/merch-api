import json
import os
import logging

from flask import Response, request, session
from flask_httpauth import HTTPBasicAuth
from flask_restful import Resource

from api.database.models import Product, Category, Inventory
from api.database.db import db
from api.libs.db_utils import run_db_action, get_item_from_db


AUTH = HTTPBasicAuth()


if __name__ != '__main__':
    app_log = logging.getLogger()
    gunicorn_logger = logging.getLogger('gunicorn.error')
    log_level = os.environ.get('LOG_LEVEL', 'INFO')
    app_log.setLevel(log_level)


@AUTH.verify_password
def verify_password(username, password):
    api_pwd = os.environ.get("API_PASSWORD")
    app_log.info("Verifying %s", username)
    if password.strip() == api_pwd:
        verified = True
    else:
        app_log.info('Access Denied')
        verified = False
    return verified


def get_product(name):
    product = get_item_from_db('product', {"name": name})
    if product:
        app_log.info('get_product Found %s', name)
        app_log.debug('Prod: %s', dir(product))
        product_data = product_to_dict(product)
        return product_data


def check_category_status(category):
    category = get_item_from_db('category', {"name": category})
    if category:
        return category.is_active


def product_to_dict(product):
    inventory = inventory_to_dict(product.inventory)
    product_dict = {
        'name': product.name,
        'sku': product.id,
        'has_sizes': product.category.has_sizes,
        'sizes': product.category.has_sizes,
        'category': product.category.name,
        'description': product.description,
        'price': product.price,
        'image_name': product.image_name,
        'image_path': product.image_path,
        'inventory': inventory
    }
    return product_dict


def inventory_to_dict(inventory):
    if inventory.has_sizes:
        inventory_dict = {
            'small': inventory.small,
            'medium': inventory.medium,
            'large': inventory.large,
            'xl': inventory.xl,
            'xxl': inventory.xxl
        }
    else:
        inventory_dict = {}
    inventory_dict['has_sizes'] = inventory.has_sizes
    inventory_dict['total'] = inventory.total
    return inventory_dict


def get_active_products_by_category(category):
    if check_category_status(category):
        # products = Product.query.filter(Category.name == category).all()
        product_list = []
        products = Product.query.filter(Product.category.has(name=category)).all()
        app_log.info('PRODUCTS: %s', products)
        if products:
            for product in products:
                product_list.append(product_to_dict(product))
        app_log.info(products[0].category)
        return product_list


def get_category(name):
    category = get_item_from_db('category', {"name": name})
    if category:
        info = {
            'id': category.name
        }
        return info


def get_all_categories():
    categories = Category.query.filter_by().all()
    if categories:
        app_log.info('CATEGORIES: %s', categories)
        return categories


def create_product(request):
    body = request.get_json()
    name = body['name']
    sku = body['sku']
    description = body['description']
    # category = body['category']
    is_active = body['is_active']
    price = body['price']
    if not get_product(name):
        category = Category.query.filter_by(name=body['category']).first()
        inventory = Inventory(name=name, has_sizes=category.has_sizes)
        db.session.add(inventory)
        db.session.commit()
        product = Product(
            name=name,
            is_active=is_active,
            category_id=category.name,
            inventory_id=inventory.name,
            description=description,
            price=price,
            sku=sku,
            image_name=body['image_name'],
            image_path=body['image_path']
        )
        db.session.add(product)
        db.session.commit()
    product = get_product(name)
    if product:
        return product


def delete_product(product_name):
    product = Product.query.filter_by(name=product_name).first()
    if product:
        db.session.delete(product)
        db.session.commit()


def update_product(product_name):
    product = Product.query.filter_by(name=product_name).first()
    if product:
        product.price = 88.88
        db.session.add(product)
        db.session.commit()


class ProductAPI(Resource):
    def post(self):
        product = create_product(request)
        if product:
            return Response(status=201)
        else:
            return Response(status=500)

    def get(self):
        body = request.get_json()
        name = body['name']
        product = get_product(name)
        if product:
            return Response(status=200)
        else:
            return Response(status=404)

    def delete(self):
        body = request.get_json()
        app_log.info('DELETING %s', body['name'])
        delete_product(body['name'])
        product = get_product(body['name'])
        if product:
            return Response(status=500)
        else:
            return Response(status=204)

    def put(self):
        body = request.get_json()
        name = body['name']
        product = update_product(name)
        if product:
            return Response(status=200)
        else:
            return Response(status=404)

    def options(self, location):
        app_log.info('- MerchAPI | OPTIONS | %s', location)
        return '', 200


class ProductsAPI(Resource):
    def get(self, category):
        products = get_active_products_by_category(category)
        if products:
            products = json.dumps(products)
            return Response(products, mimetype='application/json', status=200)
        else:
            return Response(status=404)
