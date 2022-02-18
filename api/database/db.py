import os
from flask_sqlalchemy import SQLAlchemy

from api.libs.logging import init_logger

DB = SQLAlchemy()
LOG_LEVEL= os.environ.get('LOG_LEVEL')
LOG = init_logger(log_level=LOG_LEVEL)


def init_database(app):
    DB.init_app(app=app)
    with app.app_context():
        try:
            DB.create_all()
        except Exception as err:
            LOG.error('Error initializing DBs: %s', err)
            raise err
