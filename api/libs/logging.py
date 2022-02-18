import logging


class MerchAPILogException(Exception):
    """Base class for log exceptions"""


def _get_formatter(log_level):
    if log_level == 'DEBUG':
        formats = [
            "%(asctime)s",
            "%(levelname)s",
            "%(module)s",
            "%(funcName)s",
            "%(message)s"
        ]
        formatter = logging.Formatter(" | ".join(formats), "%H:%M:%S")
    else:
        formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(message)s", "%Y-%m-%d %H:%M:%S")
    return formatter


def init_logger(log_level):
    if __name__ != '__main__':
        app_log = logging.getLogger()
        gunicorn_logger = logging.getLogger('gunicorn.error')
        gunicorn_logger.handlers = []
        app_log.handlers = gunicorn_logger.handlers
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(_get_formatter(log_level))
        app_log.addHandler(stream_handler)
        app_log.setLevel(log_level)
        return app_log
