from celery import Celery

from src.settings import settings


celery_app = Celery(
    "tasks",
    broker=settings.redis_url,
    include=[
        "src.tasks.tasks"
    ],
)

celery_app.conf.beat_schedule = {
    "check_notification_schedule": {
        "task": "check_notification_schedule",
        "schedule": 60.0,
    }
}
