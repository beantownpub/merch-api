import json
import os

from flask import Response, request
from flask_httpauth import HTTPBasicAuth
from flask_restful import Resource

from api.database.models import Category, Inventory, Product, ProductImage
from api.database.db import DB
from api.libs.db_utils import run_db_action, get_item_from_db
from api.libs.logging import init_logger
from api.libs.utils import (
    db_item_to_dict,
    get_product_by_slug,
    make_slug,
    make_uuid,
    get_inventory_by_id,
    total_item_inventory,
    ParamArgs
)

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

def get_product_by_sku(sku):
    product = Product.query.filter_by(sku=int(sku)).first()
    if product:
        LOG.debug('get_product Found %s', id)
        images = get_image_db_objects(product.uuid)
        images = [image.name for image in images]
        LOG.info('GET Images %s', images)
        product_data = db_item_to_dict(product)
        product_data['images'] = images
        inventory = get_inventory_by_id(product.inventory_id)
        inventory_total = total_item_inventory(inventory)
        inventory = db_item_to_dict(inventory)
        inventory['total'] = inventory_total
        product_data['inventory'] = inventory
        return product_data


def get_product(name, location):
    LOG.debug('GET | name: %s | location: %s', name, location)
    # product = get_item_from_db('product', {"name": name, "location": location})
    product = Product.query.filter_by(name=name, location=location).first()
    if product:
        LOG.debug('Found %s', name)
        product_data = db_item_to_dict(product)
        return product_data

def get_image_db_objects(product_uuid):
    images = ProductImage.query.filter_by(product_id=product_uuid).all()
    return images


def get_image_db_object(image_name):
    image = ProductImage.query.filter_by(name=image_name).first()
    return image


def check_category_status(category):
    category = get_item_from_db('category', {"name": category})
    if category:
        return category.is_active


def get_active_products_by_category(category):
    if check_category_status(category):
        # products = Product.query.filter(Category.name == category).all()
        product_list = []
        products = Product.query.filter(Product.category.has(name=category)).all()
        LOG.debug('PRODUCTS: %s', products)
        if products:
            for product in products:
                product_list.append(db_item_to_dict(product))
        LOG.debug(products[0].category)
        return product_list


def add_image(slug, location, image):
    product = get_product_by_slug(slug, location)
    if product:
        product_image = get_image_db_object(image)
        if not product_image:
            LOG.info('Adding Image %s %s %s', slug, location, image)
            product_image = ProductImage(
                name=image,
                product_id=product.uuid,
                uuid=make_uuid()
            )
            DB.session.add(product_image)
            DB.session.commit()
        else:
            product_image = update_image(image, product.uuid)
        return product_image


def update_image(image_name, product_uuid):
    image = get_image_db_object(image_name)
    if image:
        LOG.info('Updating image %s %s', image_name, product_uuid)
        image.name = image_name
        image.product_id = product_uuid
        DB.session.add(image)
        DB.session.commit()
    else:
        LOG.info('IMAGE NOT FOUND')
    return image

def create_product(request):
    body = request.get_json()
    slug = make_slug(body['name'])
    name = body['name'].lower()
    if not get_product_by_slug(slug, body['location']):
        LOG.info('Creating product %s', slug)
        category = Category.query.filter_by(name=body['category'], location=body['location']).first()
        inventory = Inventory(name=name, has_sizes=category.has_sizes)
        DB.session.add(inventory)
        DB.session.commit()
        product = Product(
            name=name,
            is_active=body['is_active'],
            category_id=category.uuid,
            inventory_id=inventory.id,
            description=body['description'],
            price=body['price'],
            sku=body['sku'],
            location=body['location'],
            image_name=body['image_name'],
            image_path=body['image_path'],
            has_sizes=category.has_sizes,
            uuid=make_uuid(),
            shipping_weight=body.get('shipping_weight'),
            slug=slug
        )
        DB.session.add(product)
        DB.session.commit()
        update_inventory(product, body['inventory'])
        if body.get('images'):
            for image in body['images']:
                img = add_image(slug, body['location'], image)
                LOG.info('Image Object: %s', img)
    product = get_product(name, body['location'])
    if product:
        return product


def delete_product(product):
    DB.session.delete(product)
    DB.session.commit()


def update_product(request):
    body = request.get_json()
    slug = make_slug(body['name'])
    product = get_product_by_slug(slug, body['location'])
    if product:
        category = Category.query.filter_by(name=body['category'], location=body['location']).first()
        product.price = 88.88
        product.name = body['name'].lower()
        product.is_active = body['is_active']
        product.category_id = category.uuid
        product.description = body['description']
        product.price = body['price']
        product.sku = body['sku']
        product.location = body['location']
        product.image_name = body['image_name']
        product.image_path = body['image_path']
        product.has_sizes = category.has_sizes
        product.slug = slug
        DB.session.add(product)
        DB.session.commit()
        update_inventory(product, body['inventory'])
        if body.get('images'):
            for image in body['images']:
                add_image(slug, body['location'], image)
        return product


def update_inventory(product, body):
    inventory = get_inventory_by_id(product.inventory_id)
    if inventory.has_sizes:
        inventory.small = body['smalls']
        inventory.medium = body['mediums']
        inventory.large = body['larges']
        inventory.xl = body['xls']
        inventory.xxl = body['xxls']
    else:
        inventory.quantity = body['quantity']
    DB.session.add(inventory)
    DB.session.commit()
    return True


class ProductAPI(Resource):
    def post(self):
        product = create_product(request)
        if product:
            return Response(status=201)
        else:
            return Response(status=500)

    def get(self):
        args = ParamArgs(request.args)
        product = get_product_by_sku(args.sku)
        if product:
            return Response(json.dumps(product), mimetype='application/json', status=200)
        else:
            return Response(status=404)

    def delete(self):
        args = ParamArgs(request.args)
        LOG.debug('DELETING %s', args.sku)
        product = Product.query.filter_by(sku=args.sku).first()
        if not product:
            return Response(status=404)
        else:
            delete_product(product)
            return Response(status=204)

    def put(self):
        LOG.info('UPDATING %s', request.get_json())
        product = update_product(request)
        if product:
            product = db_item_to_dict(product)
            return Response(json.dumps(product), status=200)
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
