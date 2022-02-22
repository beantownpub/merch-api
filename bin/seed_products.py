import argparse
import json
import os
import sys

from requests import delete, post, put
from requests.auth import HTTPBasicAuth

class SeedMerchException(Exception):
    """Base class seed expceptions"""


API_USERNAME = os.environ.get('API_USERNAME')
API_PASSWORD = os.environ.get('API_PASSWORD')
AUTH = HTTPBasicAuth(username=API_USERNAME, password=API_PASSWORD)
MERCH_API_HOST = os.environ.get('MERCH_API_HOST')
MERCH_API_PORT = os.environ.get('MERCH_API_SERVICE_PORT')
MERCH_API_PROTOCOL = os.environ.get('MERCH_API_PROTOCOL')
HEADERS = {'Content-Type': 'application/json'}

def parse_args():
    env = {"help": "The environment to seed", "type": str, "required": True}
    parser = argparse.ArgumentParser()
    parser.add_argument("-e", "--env", **env)
    return parser.parse_args()


def get_url(environment):
    if environment == "dev":
        merch_api_host = os.environ.get('MERCH_API_HOST_DEV')
        url = f"{MERCH_API_PROTOCOL}://{merch_api_host}:{MERCH_API_PORT}"
    elif environment == "prod":
        merch_api_host = os.environ.get('MERCH_API_HOST_PROD')
        url = f"{MERCH_API_PROTOCOL}://{merch_api_host}"
    else:
        raise SeedMerchException("Missing environment")
    return url


def get_products():
    with open('./bin/products.json') as f:
        products = json.load(f)
    return products


def post_item(product, url):
    url = f"{url}/v2/products"
    r = post(url, json=product, headers=HEADERS, auth=AUTH)
    if r.status_code in range(200,300):
        print("Ok Status: %s", r.status_code)
    else:
        print("POST Error Status: %s", r.status_code)
        raise SeedMerchException(r.content)


def post_category(category, url):
    r = post(url, json=category, headers=HEADERS, auth=AUTH)
    if r.status_code in range(200,300):
        print("Ok Status: %s", r.status_code)
    else:
        print("POST Error Status: %s\nURL: %s", r.status_code, url)
        raise SeedMerchException(r.content)


def create_category(category, environment):
    data = {
        "name": category["name"],
        "is_active": category["is_active"],
        "has_sizes": category["has_sizes"]
    }
    url = f'{get_url(environment)}/v1/merch/products/{category["name"]}'
    post_category(data, url)


def put_item(menu_item):
    url = 'http://localhost:5000/v1/merch/products'
    r = put(url, json=menu_item, headers=HEADERS, auth=AUTH)
    if r.status_code in range(200,300):
        print("Ok Status: %s", r.status_code)
    else:
        raise SeedMerchException(r.content)


def delete_item(menu_item):
    url = 'http://localhost:5000/v1/merch/items'
    r = delete(url, json=menu_item)
    print(r.status_code)


if __name__ == '__main__':
    print(__file__)
    args = parse_args()
    env = args.env
    url = get_url(env)
    print(f"URL: {url}")
    products = get_products()
    categories = products['categories']
    for category in categories:
        create_category(category, env)
        items = category['items']
        for i in items:
            post_item(i, url)
