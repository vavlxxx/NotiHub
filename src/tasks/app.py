import json
import logging.config
from pathlib import Path

from celery import Celery
from celery.signals import setup_logging

from src.settings import settings


@setup_logging.connect
def config_loggers(*args, **kwargs):
    basepath = Path(__file__).resolve().parent.parent.parent
    with open(basepath / "logging_config.json", "r") as f:
        config = json.load(f)
    logging.config.dictConfig(config)


celery_app = Celery(
    "tasks",
    broker=settings.redis_url,
    include=[
        "src.tasks.tasks",
        "src.tasks.beat",
    ],
)

celery_app.conf.worker_hijack_root_logger = False

celery_app.conf.beat_schedule = {
    "check_notification_schedule": {
        "task": "check_notification_schedule",
        "schedule": 60.0,
    }
}
