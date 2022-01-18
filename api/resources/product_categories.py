import json
import os
import logging

from flask import Response, request
from flask_httpauth import HTTPBasicAuth
from flask_restful import Resource

from api.database.models import Category, Product
from api.database.db import db


if __name__ != '__main__':
    app_log = logging.getLogger()
    gunicorn_logger = logging.getLogger('gunicorn.error')
    app_log.handlers = gunicorn_logger.handlers
    log_level = os.environ.get('LOG_LEVEL', 'INFO')
    app_log.setLevel(log_level)


def product_to_dict(product):
    inventory = inventory_to_dict(product.inventory)
    product_dict = {
        'name': product.name,
        'sku': product.id,
        'has_sizes': product.category.has_sizes,
        'category': product.category.name,
        'description': product.description,
        'price': product.price,
        'image_name': product.image_name,
        'image_path': product.image_path,
        'inventory': inventory
    }
    return product_dict


def category_to_dict(category):
    category_dict = {
        'name': category.name,
        'is_active': category.is_active,
        'has_sizes': category.has_sizes,
        'id': category.id
    }
    return category_dict


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


def get_category(name):
    category = Category.query.filter_by(name=name).first()
    if category:
        return category_to_dict(category)


def update_category(name, request):
    category = Category.query.filter_by(name=name).first()
    if category:
        body = request.get_json()
        category.name = body['name']
        category.is_active = body['is_active']
        category.has_sizes = body['has_sizes']
        db.session.add(category)
        db.session.commit()
        return get_category(body['name'])


def get_all_categories():
    category_list = []
    categories = Category.query.filter_by().all()
    if categories:
        for category in categories:
            category = get_category(category.name)
            category_list.append(category)
        # app_log.info('Categories: %s', category_list)
        return [x for x in category_list if x]


def get_categories_and_products():
    app_log.info('Getting all categories and products')
    category_list = []
    categories = get_all_categories()
    if categories:
        app_log.info('Categories: %s', categories)
        for cat in categories:
            app_log.info('Category: %s', cat)
            product_list = []
            products = Product.query.filter(Product.category.has(name=cat['name'])).all()
            if products:
                app_log.info('Products: %s', products)
                for product in products:
                    product_list.append(product_to_dict(product))
            cat['products'] = product_list
            category_list.append(cat)
    return category_list


def get_products(category):
    app_log.debug('Category: %s', category)
    product_list = []
    products = Product.query.filter(Product.category.has(name=category['name'])).all()
    if products:
        app_log.debug('Products: %s', products)
        for product in products:
            product_list.append(product_to_dict(product))
    return product_list



def create_category(request):
    body = request.get_json()
    name = body['name']
    is_active = body['is_active']
    has_sizes = body['has_sizes']
    if not get_category(name):
        category = Category(name=name, is_active=is_active, has_sizes=has_sizes)
        db.session.add(category)
        db.session.commit()
    category = get_category(name)
    if category:
        return category


def delete_category(category_name):
    category = Category.query.filter_by(name=category_name).first()
    if category:
        db.session.delete(category)
        db.session.commit()


class CategoriesAPI(Resource):
    def get(self):
        categories = get_categories_and_products()
        if categories:
            categories = json.dumps(categories)
            return Response(categories, mimetype='application/json', status=200)
        else:
            return Response(status=404)


class CategoryAPI(Resource):
    def post(self, category):
        app_log.info('Creating category %s', category)
        category = create_category(request)
        if category:
            return Response(status=201)
        else:
            return Response(status=500)

    def delete(self, category):
        app_log.info('DELETING %s', category)
        delete_category(category)
        category = get_category(category)
        if category:
            return Response(status=500)
        else:
            return Response(status=204)

    def get(self, category):
        app_log.debug('GET Category: %s', category)
        category = get_category(category)
        if category:
            products = json.dumps(get_products(category))
            return Response(products, mimetype='application/json', status=200)
        else:
            return Response(status=404)

    def put(self, category):
        app_log.info('Updating category %s', category)
        category = update_category(category, request)
        if category:
            return Response(status=204)
        else:
            return Response(status=500)