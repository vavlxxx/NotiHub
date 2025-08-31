from src.tasks.tasks import (
    send_email_notification,
    send_telegram_notification,
    send_push_notification,
    send_sms_notification,
)
from src.utils.enums import ContactChannelType


CELERY_TASKS = {
    ContactChannelType.EMAIL: send_email_notification,
    ContactChannelType.TELEGRAM: send_telegram_notification,
    ContactChannelType.PUSH: send_push_notification,
    ContactChannelType.SMS: send_sms_notification,
}
