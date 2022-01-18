import datetime
import logging
import os
from urllib.parse import quote_plus
from flask import Flask
from flask_restful import Api
from flask_cors import CORS
from flask_session import Session

from api.database.db import init_database
from api.resources.routes import init_routes


class MerchAPIException(Exception):
    """Base class for merch API exceptions"""


LOG_LEVEL = os.environ.get('MERCH_API_LOG_LEVEL', 'INFO')
ORIGIN_URL = os.environ.get('ORIGIN_URL', 'http://localhost:3000')
APP = Flask(__name__.split('.')[0], instance_path='/opt/app/api')
API = Api(APP)
PSQL = {
    'user': os.environ.get('DB_USER'),
    'password': os.environ.get('DB_PASSWORD'),
    'host': os.environ.get('DB_HOST'),
    'name': os.environ.get('DB_NAME'),
    'port': os.environ.get('DB_PORT')
}

MERCH_DB = [
    f"postgresql://{PSQL['user']}:{PSQL['password']}",
    f"{PSQL['host']}:{PSQL['port']}/{PSQL['name']}"
]

APP.config['SQLALCHEMY_ENGINE_OPTIONS'] = {"pool_pre_ping": True}
APP.config['SQLALCHEMY_POOL_SIZE'] = 10
APP.config['SQLALCHEMY_MAX_OVERFLOW'] = 20
APP.config['SQLALCHEMY_POOL_RECYCLE'] = 1800
APP.config['SESSION_TYPE'] = "sqlalchemy"
# APP.config['SESSION_SQLALCHEMY'] = "@".join(SESSIONS_DB)
APP.config['SESSION_SQLALCHEMY_TABLE'] = "sessions"
APP.config['SQLALCHEMY_DATABASE_URI'] = "@".join(MERCH_DB)
APP.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
APP.config['CORS_ALLOW_HEADERS'] = True
APP.config['CORS_EXPOSE_HEADERS'] = True
APP.config['SECRET_KEY'] = '3dc99e1e-bd13-4537-b5fe-b1c49082d840'
APP.permanent_session_lifetime = datetime.timedelta(days=365)

cors = CORS(
    APP,
    resources={r"/v1/*": {"origins": "localhost"}},
    supports_credentials=True
)

APP.logger.info('Initializing database')
init_database(APP)
APP.logger.info('%s DB initialized', PSQL['name'])
init_routes(API)
APP.logger.info('Routes initialized')

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
