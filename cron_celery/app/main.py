from celery import Celery
from celery.schedules import crontab

from app.config import settings

celery_app = Celery(
    settings.NAME_SCHEDULER,
    broker=settings.get_rabbit_url,
)
celery_app.conf.update(
    task_serializer=settings.SERIALIZER_FORMAT,
    accept_content=[settings.SERIALIZER_FORMAT],
    timezone=settings.TIMEZONE,
    enable_utc=True,
    worker_hijack_root_logger=False,
)
celery_app.autodiscover_tasks(['app.tasks'])

celery_app.conf.beat_schedule = {
    "notify_users": {
        "task": 'notify_users',
        "schedule": crontab(hour=12, minute=00),
    },
}
