import os

from api.database.models import Cart, CartItem, Category, Customer, Inventory, Product, Order
from api.database.db import DB
from api.libs.logging import init_logger

LOG_LEVEL= os.environ.get('LOG_LEVEL')
LOG = init_logger(LOG_LEVEL)
class MerchDBException(Exception):
    """Base class for menu database exceptions"""


TABLES = {
    "cart": Cart,
    "cart_item": CartItem,
    "category": Category,
    "customers": Customer,
    "inventory": Inventory,
    "orders": Order,
    "product": Product
}


def _db_update(item, table_name, data):
    item.name = data['name']
    item.is_active = data['is_active']
    if table_name == 'category':
        DB.session.add(item)
    elif table_name == 'cart_item':
        item.product = data['product']
        item.cart_id = data['cart_id']
        item.category_id = data['category_id']
        item.slug = data['slug']
        DB.session.add(item)
    else:
        raise MerchDBException(f"DB Table {table_name} not found")


def _db_write(table_name, data, query=None):
    LOG.debug('Writing to DB | Table: %s | Data: %s | Query: %s', table_name, data, query)
    table = TABLES.get(table_name)
    # if not get_item_from_db(table_name, query=query):
    item = table(**data)
    DB.session.add(item)


def get_item_from_db(table_name, query=None, multiple=False):
    table = TABLES.get(table_name)
    # LOG.debug('Table DIR: %s', dir(table))
    LOG.debug('DB table: %s | Query: %s', table_name, query)
    if not table:
        raise MerchDBException(f"DB Table {table_name} not found")
    if not multiple:
        item = table.query.filter_by(**query).first()
    else:
        item = table.query.filter_by(**query).all()
    return item


def run_db_action(action, item=None, data=None, table=None, query=None):
    LOG.debug('Action: %s | Table: %s | Data: %s', action, table, data)
    if action == "create":
        _db_write(data=data, table_name=table, query=query)
    elif action == "update":
        _db_update(item=item, table_name=table, data=data)
    elif action == "delete":
        if table == 'cart_item':
            item.cart = None
        DB.session.delete(item)
    else:
        raise MerchDBException(f"DB action {action} not found")
    DB.session.commit()
