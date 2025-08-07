from src.tasks.app import celery_app


@celery_app.task(name="send_notification")
def send_notification():
    ...
