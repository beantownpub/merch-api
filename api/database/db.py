import os
import socket

from flask_mongoengine import MongoEngine
from flask_mongoengine.connection import mongoengine

import logging


class MongoHostException(Exception):
    """Base class for mongodb host exceptions"""


db = MongoEngine()
mongoengine.disconnect()


def get_mongo_host():
    mongo_host = os.environ.get('MONGO_HOST')
    if not mongo_host:
        host = socket.gethostname()
        if host.endswith('local') or host.endswith('internal'):
            mongo_host = 'localhost'
        else:
            err_msg = [
                "MongoDB hostname or address Not Found",
                "Set -e MONGO_HOST=<hostname or address> when starting API container"
            ]
            err_msg = '\n'.join(err_msg)
            logging.error(err_msg)
            raise MongoHostException(err_msg)
    return mongo_host


def init_database(app):
    db.init_app(app)
