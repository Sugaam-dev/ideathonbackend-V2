from celery import Celery
from app.config import settings
celery_app = Celery(
    "ideathon_tasks",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL
)
# Standard Celery Configuration
celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
    imports=["app.core.email"]  # Autoload the email tasks
)