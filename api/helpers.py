import os

from api.libs.logging import init_logger

LOG = init_logger(os.environ.get('LOG_LEVEL'))


def log_request(func):
    def _request(*args, **kwargs):
        if kwargs.get('request'):
            request = kwargs['request']
            session = kwargs['session']
            LOG.debug(f"URL: {request.url}")
            LOG.debug(f"SID: {session.sid}")
        response = func(*args, **kwargs)
        return response
    return _request
