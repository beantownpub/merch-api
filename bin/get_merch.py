import argparse
import json
import os
import sys

from requests import get
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
    env = {"help": "The environment to test", "type": str, "required": True}
    location = {"help": "The location to get items from", "type": str, "required": True}
    parser = argparse.ArgumentParser()
    parser.add_argument("-e", "--env", **env)
    parser.add_argument("-l", "--location", **location)
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


def main(environment, location):
    url = get_url(environment)
    print(f"URL: {url}")
    req = get(f"{url}/v2/merch?location={location}", headers=HEADERS, auth=AUTH)
    print(req.status_code)
    print(json.dumps(req.json(), indent=2))

if __name__ == '__main__':
    args = parse_args()
    print(args)
    env = args.env
    location = args.location
    main(env, location)
