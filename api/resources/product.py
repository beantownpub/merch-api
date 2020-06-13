import logging
from flask import Response, request
from flask_restful import Resource

from api.database.models import Product

app_log = logging.getLogger()

if __name__ != '__main__':
    gunicorn_logger = logging.getLogger('gunicorn.error')
    app_log.handlers = gunicorn_logger.handlers
    app_log.setLevel('INFO')


class ProductsAPI(Resource):
    def get(self):
        products = Product.objects().to_json()
        return Response(products, mimetype='application/json', status=200)

    def post(self):
        body = request.get_json()
        logging.info(body)
        product = Product(**body).save()
        _id = product.id
        return {'id': str(_id)}, 200

    def delete(self):
        sku = request.get_json()['sku']
        Product.objects.get(sku=sku).delete()
        return '', 204


class ProductAPI(Resource):
    def get(self, _id):
        product = Product.objects.get(id=_id).to_json()
        return Response(product, mimetype="application/json", status=200)

    def put(self, _id):
        body = request.get_json()
        Product.objects.get(id=_id).update(**body)
        return '', 200

    def delete(self, sku):
        Product.objects.get(sku=sku).delete()
        return '', 200


class CategoryAPI(Resource):
    def get(self, category):
        products = Product.objects(category=category).to_json()
        app_log.info('- CategoryAPI | GET | Category: %s', category)
        app_log.info('- CategoryAPI | GET | Products: %s', products)
        return Response(products, mimetype='application/json', status=200)
