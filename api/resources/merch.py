import json
import os

from flask import Response, request
from flask_httpauth import HTTPBasicAuth
from flask_restful import Resource

from api.database.models import Category, Product
from api.libs.logging import init_logger
from api.libs.utils import db_item_to_dict, ParamArgs

AUTH = HTTPBasicAuth()
LOG_LEVEL= os.environ.get('LOG_LEVEL')
LOG = init_logger(log_level=LOG_LEVEL)


@AUTH.verify_password
def verify_password(username, password):
    api_pwd = os.environ.get("API_PASSWORD")
    if password.strip() == api_pwd:
        verified = True
    else:
        verified = False
    return verified


def _get_categories(location, active=True):
    categories = Category.query.filter_by(location=location, is_active=active).all()
    LOG.debug('_get_categories | Active: %s | %s', active, categories)
    return categories

def _get_products_by_category(category, location, active=True):
    products = Product.query.filter_by(category_id=category, location=location, is_active=active).all()
    LOG.debug('_get_products_by_category | Active: %s | %s', active, products)
    return products


class MerchAPI(Resource):
    @AUTH.login_required
    def get(self):
        args = ParamArgs(request.args)
        LOG.debug('Args | %s', args)
        category_list = []
        categories = _get_categories(args.location)
        if categories:
            for category in categories:
                product_list = []
                products = _get_products_by_category(category.uuid, args.location)
                category = db_item_to_dict(category)
                for product in products:
                    product_list.append(db_item_to_dict(product))
                    category['products'] = product_list
                category_list.append(category)
            # LOG.debug('MerchAPI | GET | Categories INFO: %s', category_list)
        resp = {"status": 200, "response": json.dumps(category_list), "mimetype": "application/json"}
        return Response(**resp)
