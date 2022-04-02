import json
import os
from redis import Redis
from .logging import init_logger

LOG_LEVEL= os.environ.get('LOG_LEVEL')
LOG = init_logger(LOG_LEVEL)

HOST = os.environ.get('REDIS_HOST', 'localhost')
PORT = os.environ.get('REDIS_PORT', 6379)
CLIENT = Redis(host=HOST, port=PORT)


def get_cache(key_name):
    LOG.info('Checking REDIS cache | Key | %s', key_name)
    data = CLIENT.get(key_name)
    return data


def set_cache(key_name, data):
    LOG.debug('Setting REDIS cache | Key | %s | Data  | %s', key_name, data)
    CLIENT.set(key_name, json.dumps(data), ex=86400)


def delete_cache(key_name):
    LOG.info('Deleting REDIS cache %s', key_name)
    CLIENT.delete(key_name)