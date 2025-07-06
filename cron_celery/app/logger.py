import logging

from celery.signals import after_setup_logger


logger = logging.getLogger(__name__)


@after_setup_logger.connect
def setup_loggers(logger, *args, **kwargs):
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh = logging.FileHandler('logs.log')
    fh.setFormatter(formatter)
    logger.addHandler(fh)