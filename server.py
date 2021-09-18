import datetime
import os

from urllib.parse import quote_plus
from flask_session import Session

from api.app import APP

APP.secret_key = os.environ.get('3dc99e1e-bd13-4537-b5fe-b1c49082d840')
APP.permanent_session_lifetime = datetime.timedelta(days=365)

if __name__ == "__main__":
    APP.config.from_object(__name__)
    Session(APP)
    APP.debug = True
    APP.run()
