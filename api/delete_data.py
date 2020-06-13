import os
import socket
from urllib.parse import quote_plus
from pymongo import MongoClient


class MerchAPIException(Exception):
    """Base class for merch API exceptions"""


def _mongo_host():
    mongo_host = os.environ.get('MONGO_HOST')
    if not mongo_host:
        if socket.gethostname().endswith('local'):
            mongo_host = 'localhost'
        else:
            err_msg = [
                "MongoDB hostname or address Not Found",
                "Set -e MONGO_HOST=<hostname or address> when starting API container"
            ]
            raise MerchAPIException('\n'.join(err_msg))
    return mongo_host


def _mongo_client():
    mongo_host = os.environ.get('MONGO_HOST')
    pw = os.environ.get('MONGO_ADMIN_PW')
    if not mongo_host:
        if socket.gethostname().endswith('local'):
            mongo_host = 'localhost'
        else:
            err_msg = [
                "MongoDB hostname or address Not Found",
                "Set -e MONGO_HOST=<hostname or address> when starting API container"
            ]
            raise MerchAPIException('\n'.join(err_msg))
    uri = "mongodb://%s:%s@%s" % (quote_plus('admin'), quote_plus(pw), mongo_host)
    return MongoClient(uri)


CLIENT = _mongo_client()


def _list_dbs():
    print(CLIENT.list_database_names())


def _delete_sessions():
    db = CLIENT['merch']['cart_sessions']
    db.delete_many({})


def _delete_carts():
    db = CLIENT['merch']['shopping_cart']
    db.delete_many({})


def _delete_cart_items():
    db = CLIENT['merch']['cart_item']
    db.delete_many({})


def _delete_products():
    db = CLIENT['merch']['products']
    db.delete_many({})


def delete_data():
    _delete_cart_items()
    _delete_carts()
    _delete_sessions()


if __name__ == '__main__':
    _list_dbs()
    # delete_data()
