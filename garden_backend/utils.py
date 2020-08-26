import inspect
import logging

LOG_FORMAT = '%(asctime)s %(levelname)8s [%(filename)s:%(lineno)d:%(funcName)s] %(message)s'

def setup_logger(name=None):
    if name is None:
        name = inspect.stack()[1].filename
    logger = logging.getLogger(name)
    handler = logging.StreamHandler()
    formatter = logging.Formatter(LOG_FORMAT)
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger
