import requests

from app.config import settings
from app.logger import logger
from app.main import celery_app


@celery_app.task(
    name='notify_users',
    bind=True,
    max_retries=settings.MAX_RETRIES,
    default_retry_delay=settings.DEF_RETRY_DELAY,
)
def notify_users(self):
    """Задача по уведомлению клиентов о статусе подписки."""
    url = (f'{settings.get_backend_url}/'
           f'{settings.NOTIFY_PATH}/{settings.SUBSCRIPTION_PATH}')
    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.RequestException as error:
        logger.error(f'Ошибка обращения к {url}: {error}')
        self.retry(exc=error)
    else:
        logger.info('Запрос на уведомление клиентов отправлен успешно.')
    return True
