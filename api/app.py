import logging
import os
from urllib.parse import quote_plus
from flask import Flask
from flask_restful import Api
from flask_cors import CORS

from api.database.db import init_database
from api.resources.routes import init_routes


class MerchAPIException(Exception):
    """Base class for merch API exceptions"""


LOG_LEVEL = os.environ.get('MERCH_API_LOG_LEVEL', 'INFO')
ORIGIN_URL = os.environ.get('ORIGIN_URL', 'https://beantown.jalgraves.com')
APP = Flask(__name__.split('.')[0], instance_path='/opt/app/api')
API = Api(APP)

APP.config['CORS_ALLOW_HEADERS'] = True
APP.config['CORS_EXPOSE_HEADERS'] = True
APP.config['MONGODB_SETTINGS'] = {
    'host': os.environ.get('MONGO_HOST'),
    'db': os.environ.get('MONGO_DB'),
    'username': os.environ.get('MONGO_USER'),
    'password':os.environ.get('MONGO_PW'),
    'connect': False
}

cors = CORS(
    APP,
    resources={r"/v1/*": {"origins": "localhost"}},
    supports_credentials=True
)

init_database(APP)
init_routes(API)

if __name__ != '__main__':
    gunicorn_logger = logging.getLogger('gunicorn.error')
    APP.logger.handlers = gunicorn_logger.handlers
    APP.logger.setLevel(LOG_LEVEL)


@APP.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', ORIGIN_URL)
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    return response
