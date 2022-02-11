import os
import requests

from requests.auth import HTTPBasicAuth
from api.libs.logging import init_logger

API_USERNAME = os.environ.get('API_USERNAME')
API_PASSWORD = os.environ.get('API_PASSWORD')
AUTH = HTTPBasicAuth(username=API_USERNAME, password=API_PASSWORD)
CONTACT_API_HOST = os.environ.get('CONTACT_API_HOST')
CONTACT_API_PORT = os.environ.get('CONTACT_API_SERVICE_PORT')
CONTACT_API_PROTOCOL = os.environ.get('CONTACT_API_PROTOCOL')
HEADERS = {'Content-Type': 'application/json'}
LOG = init_logger(os.environ.get('LOG_LEVEL'))
URL = f"{CONTACT_API_PROTOCOL}://{CONTACT_API_HOST}:{CONTACT_API_PORT}/v1/contact/merch"


def send_order_confirmation(order_data):
    req = requests.post(URL, auth=AUTH, headers=HEADERS, json=order_data)
    LOG.info('Status: %s', req.status_code)
    return req