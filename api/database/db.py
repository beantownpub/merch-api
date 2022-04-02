import os
from flask_sqlalchemy import SQLAlchemy

from api.libs.logging import init_logger

from flask_migrate import Migrate

DB = SQLAlchemy()
MIGRATE = Migrate()
LOG_LEVEL= os.environ.get('LOG_LEVEL')
LOG = init_logger(LOG_LEVEL)


def init_database(app):
    DB.init_app(app=app)
    MIGRATE.init_app(app, DB)
    with app.app_context():
        try:
            DB.create_all()
        except Exception as err:
            LOG.error('Error initializing DBs: %s', err)
            raise err
