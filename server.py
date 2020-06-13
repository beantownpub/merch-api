import datetime
import os

from urllib.parse import quote_plus
from flask_session import Session, MongoDBSessionInterface
from flask_pymongo import PyMongo

from api.app import APP

APP.secret_key = os.environ.get('SESSION_KEY')
MONGO_HOST = os.environ.get('MONGO_HOST')
MONGO_USER = quote_plus(os.environ.get('MONGO_USER'))
MONGO_DB = quote_plus(os.environ.get('MONGO_DB'))
MONGO_PW = quote_plus(os.environ.get('MONGO_PW'))
URI = f"mongodb://{MONGO_USER}:{MONGO_PW}@{MONGO_HOST}/{MONGO_DB}"
MONGO = PyMongo(APP, uri=URI)
APP.session_interface = MongoDBSessionInterface(MONGO.cx, 'merch', 'cart-sessions', key_prefix='cart-')
APP.permanent_session_lifetime = datetime.timedelta(days=365)

if __name__ == "__main__":
    APP.config.from_object(__name__)
    Session(APP)
    APP.debug = True
    APP.run()
