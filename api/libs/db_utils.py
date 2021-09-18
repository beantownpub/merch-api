import logging

from api.database.models import Product, Category, Inventory
from api.database.db import db


class MerchDBException(Exception):
    """Base class for menu database exceptions"""


TABLES = {
    "product": Product,
    "category": Category,
    "inventory": Inventory
}


def _db_update(item, table_name, body):
    item.name = body['name']
    item.is_active = body['is_active']
    if table_name == 'category':
        db.session.add(item)
    elif table_name == 'food_item':
        item.description = body['description']
        item.price = body['price']
        item.category_id = body['category_id']
        item.slug = body['slug']
        db.session.add(item)
    else:
        raise MerchDBException(f"DB Table {table_name} not found")


def _db_write(table_name, body):
    table = TABLES.get(table_name)
    if not get_item_from_db(table_name, body['name']):
        item = table(**body)
        db.session.add(item)


if __name__ != '__main__':
    app_log = logging.getLogger()
    gunicorn_logger = logging.getLogger('gunicorn.error')
    app_log.handlers = gunicorn_logger.handlers


def get_item_from_db(table_name, item_name):
    table = TABLES.get(table_name)
    if not table:
        raise MerchDBException(f"DB Table {table_name} not found")
    item = table.query.filter_by(name=item_name).first()
    return item


def run_db_action(action, item=None, body=None, table=None):
    if action == "create":
        _db_write(body=body, table_name=table)
    elif action == "update":
        _db_update(item=item, table_name=table, body=body)
    elif action == "delete":
        db.session.delete(item)
    else:
        raise MerchDBException(f"DB action {action} not found")
    db.session.commit()
