from urllib.parse import quote_plus
from flask_session import Session

from api.app import APP

if __name__ == "__main__":
    APP.config.from_object(__name__)
    Session(APP)
    APP.debug = True
    APP.run()
