import logging
import os

from api.database.models import Cart, CartItem, Category, Customer, Inventory, Product, Order
from api.database.db import db


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
        db.session.add(item)
    elif table_name == 'cart_item':
        item.product = data['product']
        item.cart_id = data['cart_id']
        item.category_id = data['category_id']
        item.slug = data['slug']
        db.session.add(item)
    else:
        raise MerchDBException(f"DB Table {table_name} not found")


def _db_write(table_name, data, query=None):
    app_log.info('Writing to DB | Table: %s | Data: %s | Query: %s', table_name, data, query)
    table = TABLES.get(table_name)
    # if not get_item_from_db(table_name, query=query):
    item = table(**data)
    db.session.add(item)


def _delete_cart_association(cart_item):
    app_log.info('Cart DIR: %s', dir(cart_item.cart))
    #query = {"cart_item_id": cart_item.id, "cart_id": cart_item.cart_id}
    # cart_association = get_item_from_db('cart_association', query=query)
    # app_log.info('Deleting DB association: %s', cart_association)
    cart_item.cart.clear()
    # db.session.expire(cart_association)
    # db.session.commit()


if __name__ != '__main__':
    app_log = logging.getLogger()
    gunicorn_logger = logging.getLogger('gunicorn.error')
    app_log.handlers = gunicorn_logger.handlers
    log_level = os.environ.get('LOG_LEVEL', 'INFO')
    app_log.setLevel(log_level)


def get_item_from_db(table_name, query=None, multiple=False):
    table = TABLES.get(table_name)
    # app_log.info('Table DIR: %s', dir(table))
    app_log.info('Table: %s | Query: %s', table_name, query)
    if not table:
        raise MerchDBException(f"DB Table {table_name} not found")
    if not multiple:
        item = table.query.filter_by(**query).first()
    else:
        item = table.query.filter_by(**query).all()
    return item


def run_db_action(action, item=None, data=None, table=None, query=None):
    app_log.info('Action: %s | Table: %s | Data: %s', action, table, data)
    if action == "create":
        _db_write(data=data, table_name=table, query=query)
    elif action == "update":
        _db_update(item=item, table_name=table, data=data)
    elif action == "delete":
        if table == 'cart_item':
            # _delete_cart_association(cart_item=item)
            item.cart = None
        db.session.delete(item)
    else:
        raise MerchDBException(f"DB action {action} not found")
    db.session.commit()
