import logging
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

if __name__ != '__main__':
    app_log = logging.getLogger()
    gunicorn_logger = logging.getLogger('gunicorn.error')
    app_log.handlers = gunicorn_logger.handlers
    app_log.setLevel('INFO')


def init_database(app):
    db.init_app(app=app)
    with app.app_context():
        try:
            db.create_all()
        except Exception as err:
            app_log.error('\n* * * Error setting up DBs * * *\n')
            raise err
