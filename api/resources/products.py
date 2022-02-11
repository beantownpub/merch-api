import json
import os
import logging

from flask import Response, request, session
from flask_httpauth import HTTPBasicAuth
from flask_restful import Resource

from api.database.models import Product, Category, Inventory
from api.database.db import DB
from api.libs.db_utils import run_db_action, get_item_from_db
from api.libs.logging import init_logger

AUTH = HTTPBasicAuth()


LOG_LEVEL= os.environ.get('LOG_LEVEL')
LOG = init_logger(log_level=LOG_LEVEL)


@AUTH.verify_password
def verify_password(username, password):
    api_pwd = os.environ.get("API_PASSWORD")
    LOG.info("Verifying %s", username)
    if password.strip() == api_pwd:
        verified = True
    else:
        LOG.info('Access Denied')
        verified = False
    return verified


def get_product(name):
    product = get_item_from_db('product', {"name": name})
    if product:
        LOG.info('get_product Found %s', name)
        LOG.debug('Prod: %s', dir(product))
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
        LOG.info('PRODUCTS: %s', products)
        if products:
            for product in products:
                product_list.append(product_to_dict(product))
        LOG.info(products[0].category)
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
        LOG.info('CATEGORIES: %s', categories)
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
        DB.session.add(inventory)
        DB.session.commit()
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
        DB.session.add(product)
        DB.session.commit()
    product = get_product(name)
    if product:
        return product


def delete_product(product_name):
    product = Product.query.filter_by(name=product_name).first()
    if product:
        DB.session.delete(product)
        DB.session.commit()


def update_product(product_name):
    product = Product.query.filter_by(name=product_name).first()
    if product:
        product.price = 88.88
        DB.session.add(product)
        DB.session.commit()


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
        LOG.info('DELETING %s', body['name'])
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
        LOG.info('- MerchAPI | OPTIONS | %s', location)
        return '', 200


class ProductsAPI(Resource):
    def get(self, category):
        products = get_active_products_by_category(category)
        if products:
            products = json.dumps(products)
            return Response(products, mimetype='application/json', status=200)
        else:
            return Response(status=404)
