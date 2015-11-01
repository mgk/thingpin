import logging
import logging.handlers
import sys


def Logger(name='thingpin', level=logging.INFO, log_file=None):
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.propagate = False

    if log_file is not None:
        handler = logging.handlers.RotatingFileHandler(
            log_file, maxBytes=10 * 1024 * 1024, backupCount=10)
        handler.setFormatter(logging.Formatter(
            '%(asctime)s %(name)s %(process)d %(levelname)s %(message)s'))
    else:
        handler = logging.StreamHandler(stream=sys.stdout)
        handler.setFormatter(logging.Formatter(
            '%(asctime)s %(name)s %(levelname)s %(message)s'))

    logger.addHandler(handler)
    return logger
