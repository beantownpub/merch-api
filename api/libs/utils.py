import os
import uuid
from .db_utils import get_item_from_db, run_db_action
from .logging import init_logger
from api.database.models import Product, Inventory

LOG_LEVEL= os.environ.get('LOG_LEVEL')
LOG = init_logger(LOG_LEVEL)

def make_uuid():
    return str(uuid.uuid4())


def make_slug(name):
    slug = name.lower().replace(' ', '-').replace('.', '').replace('&', 'and').strip('*')
    return slug

class ParamArgs:
    def __init__(self, args):
        self.args = args
        self.cart_id = args.get('cart_id')
        self.location = args.get('location')
        self.name = args.get('name')
        self.sku = args.get('sku')
        self.id = args.get('id')

    def __repr__(self):
        return repr(self.map)

    @property
    def map(self):
        args_dict = {
            "cart_id": self.cart_id,
            "location": self.location,
            "name": self.name,
            "id": self.id,
            "sku": self.sku
        }
        return args_dict

def db_item_to_dict(item):
    LOG.debug('db_item_to_dict | %s', item)
    item_dict = item.__dict__
    LOG.debug('item dict | %s', item_dict)
    if item_dict.get('_sa_instance_state'):
        del item_dict['_sa_instance_state']
    if item_dict.get('creation_date'):
        del item_dict['creation_date']
    return item_dict

def cart_item_to_dict(cart_item):
    item_data = {
        "quantity": cart_item.item_count,
        "sku": cart_item.product.id,
        "name": cart_item.product.name,
        "price": cart_item.product.price
    }
    category = get_item_from_db('category', query={"uuid": cart_item.product.category_id})
    if category.has_sizes:
        item_data["size"] = cart_item.size
    item_data['total'] = item_data['quantity'] * item_data['price']
    return item_data


def get_cart_items(cart_id):
    cart_data = {
        'cart_items': [],
        'cart_id': cart_id
    }
    cart = get_item_from_db('cart', query={"cart_id": cart_id})
    query = {"cart_id": cart.cart_id}
    cart_items = get_item_from_db('cart_item', query=query, multiple=True)
    for item in cart_items:
        if item.product:
            item_data = cart_item_to_dict(item)
            cart_data['cart_items'].append(item_data)
    cart_data['total'] = calculate_cart_total(cart)
    return cart_data


def calculate_cart_total(cart):
    item_prices = []
    cart_items = get_item_from_db('cart_item', query={"cart_id": cart.cart_id}, multiple=True)
    for item in cart_items:
        if item.product:
            item_count = item.item_count
            price = item.product.price
            item_prices.append(item_count * price)
    return round(sum(item_prices), 2)


def get_product_by_slug(slug, location):
    LOG.debug('Slug: %s | Location: %s', slug, location)
    product = Product.query.filter_by(slug=slug, location=location).first()
    LOG.debug('Product: %s', product)
    return product


def total_item_inventory(inventory):
    """Get the total number units in stock for a single item"""
    if inventory.has_sizes:
        total = sum([inventory.small, inventory.medium, inventory.large, inventory.xl, inventory.xxl])
    else:
        total = inventory.quantity
    return total

def get_inventory_by_id(id):
    LOG.debug('ID: %s ', id)
    inventory = Inventory.query.filter_by(id=id).first()
    LOG.debug('Inventory: %s', inventory)
    return inventory