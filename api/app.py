import datetime
import os
from flask import Flask
from flask_restful import Api
from flask_cors import CORS

from api.database.db import init_database
from api.libs.logging import init_logger
from api.resources.routes import init_routes


class MerchAPIException(Exception):
    """Base class for merch API exceptions"""


LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
LOG = init_logger(LOG_LEVEL)
LOG.info('Logging level %s initialized', LOG_LEVEL)
ORIGIN_URL = os.environ.get('FRONTEND_ORIGIN_URL')
APP = Flask(__name__.split('.')[0], instance_path='/opt/app/api')
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
APP.config['SQLALCHEMY_DATABASE_URI'] = "@".join(MERCH_DB)
APP.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
APP.config['CORS_ALLOW_HEADERS'] = True
APP.config['CORS_EXPOSE_HEADERS'] = True
# APP.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY')
# APP.permanent_session_lifetime = datetime.timedelta(days=365)

cors = CORS(
    APP,
    resources={r"/v1/*": {"origins": "localhost"}},
    supports_credentials=True
)

API = Api(APP)
LOG.info('Initializing database')
init_database(APP)
LOG.info('%s DB initialized', PSQL['name'])
init_routes(API)
LOG.info('Routes initialized')


@APP.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', ORIGIN_URL)
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    return response
