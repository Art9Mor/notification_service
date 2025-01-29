from celery import Celery

from .config import settings

celery_app = Celery(
    'notification_tasks',
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_BACKEND_URL
)
