import logging
import os
from datetime import datetime
from logging.handlers import TimedRotatingFileHandler

from celery.signals import after_setup_logger

from app.config import settings

logger = logging.getLogger(__name__)


@after_setup_logger.connect
def setup_loggers(logger, *args, **kwargs):
    os.makedirs(settings.LOG_DIR, exist_ok=True)
    log_filename = os.path.join(
        settings.LOG_DIR,
        f'celery_{datetime.now().date()}.log',
    )

    handler = TimedRotatingFileHandler(
        filename=log_filename,
        when='midnight',
        interval=1,
        backupCount=7,
        encoding='utf-8',
        delay=True
    )

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    handler.setLevel(logging.INFO)

    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
