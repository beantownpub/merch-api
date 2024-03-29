import json
import os

from flask import Response, request
from flask_httpauth import HTTPBasicAuth
from flask_restful import Resource

from api.database.models import Category, Product
from api.database.db import DB
from api.libs.logging import init_logger
from api.libs.utils import db_item_to_dict, make_uuid, ParamArgs

LOG_LEVEL= os.environ.get('LOG_LEVEL')
LOG = init_logger(log_level=LOG_LEVEL)


def get_category(name, location):
    category = Category.query.filter_by(name=name, location=location).first()
    if category:
        return db_item_to_dict(category)


def update_category(name, request):
    category = Category.query.filter_by(name=name).first()
    if category:
        body = request.get_json()
        category.name = body['name']
        category.is_active = body['is_active']
        category.has_sizes = body['has_sizes']
        DB.session.add(category)
        DB.session.commit()
        return get_category(body['name'])


def get_all_categories():
    category_list = []
    categories = Category.query.filter_by().all()
    if categories:
        for category in categories:
            category = get_category(category.name)
            category_list.append(category)
        # LOG.info('Categories: %s', category_list)
        return [x for x in category_list if x]


def get_categories_and_products():
    LOG.info('Getting all categories and products')
    category_list = []
    categories = get_all_categories()
    if categories:
        LOG.info('Categories: %s', categories)
        for cat in categories:
            LOG.info('Category: %s', cat)
            product_list = []
            products = Product.query.filter(Product.category.has(name=cat['name'])).all()
            if products:
                LOG.info('Products: %s', products)
                for product in products:
                    product_list.append(db_item_to_dict(product))
            cat['products'] = product_list
            category_list.append(cat)
    return category_list


def get_products(category):
    LOG.debug('Category: %s', category)
    product_list = []
    products = Product.query.filter(Product.category.has(name=category['name'])).all()
    if products:
        LOG.debug('Products: %s', products)
        for product in products:
            product_list.append(db_item_to_dict(product))
    return product_list



def create_category(request):
    body = request.get_json()
    name = body['name']
    is_active = body['is_active']
    has_sizes = body['has_sizes']
    location = body['location']
    if not get_category(name, location):
        category = Category(
            name=name.lower(),
            is_active=is_active,
            has_sizes=has_sizes,
            location=location,
            uuid=make_uuid()
        )
        DB.session.add(category)
        DB.session.commit()
    category = get_category(name, location)
    if category:
        return category


def delete_category(category_name):
    category = Category.query.filter_by(name=category_name).first()
    if category:
        DB.session.delete(category)
        DB.session.commit()


class CategoriesAPI(Resource):
    def get(self):
        categories = get_categories_and_products()
        if categories:
            categories = json.dumps(categories)
            return Response(categories, mimetype='application/json', status=200)
        else:
            return Response(status=404)


class CategoryAPI(Resource):
    def post(self):
        LOG.debug('Creating category %s', request.get_json())
        body = request.get_json()
        category = get_category(body['name'], body['location'])
        if category:
            resp = {"status": 200, "response": "Category already exists"}
            return Response(**resp)
        category = create_category(request)
        if category:
            return Response(status=201)
        else:
            return Response(status=500)

    def delete(self):
        LOG.debug('DELETING %s', category)
        delete_category(category)
        category = get_category(category)
        if category:
            return Response(status=500)
        else:
            return Response(status=204)

    def get(self):
        args = ParamArgs(request.args)
        LOG.debug('GET Category: %s', args)
        category = get_category(args.name, args.location)
        if category:
            category = json.dumps(category)
            return Response(category, mimetype='application/json', status=200)
        else:
            return Response(status=404)

    def put(self, category):
        LOG.debug('Updating category %s', category)
        category = update_category(category, request)
        if category:
            return Response(status=204)
        else:
            return Response(status=500)
