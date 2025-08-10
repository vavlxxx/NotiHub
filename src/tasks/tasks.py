import ssl
import smtplib
import asyncio
import aiohttp
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from src.tasks.app import celery_app
from src.settings import settings
from src.utils.db_manager import DB_Manager
from src.schemas.notifications import NotificationLogAddDTO
from src.db import sessionmaker_null_pool


async def insert_result_into_database(data: NotificationLogAddDTO):
    async with DB_Manager(session_factory=sessionmaker_null_pool) as db:
        await db.notification_logs.add(data)
        await db.commit()


async def send_telegram_message(contact: str, msg: str):
    body = {"chat_id": contact, "text": msg}
    async with aiohttp.ClientSession() as session:
        async with session.post(f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage", json=body) as response:
            ...

    obj = NotificationLogAddDTO(receiver=contact, message=msg, response=str(response.status))
    await insert_result_into_database(obj)


@celery_app.task(name="send_to_telegram")
def send_telegram_notification(contact: str, msg: str):
    asyncio.run(send_telegram_message(contact, msg))


@celery_app.task(
    bind=True,
    name="send_to_email", 
    max_retries=3,
)
def send_email_notification(self, contact: str, msg: str):
    message = MIMEMultipart("alternative")
    message["Subject"] = "🔔 NotiHub | Уведомление"
    message["From"] = settings.SMTP_USER
    message["To"] = contact
    message.attach(MIMEText(msg, "plain"))
    msg_ = message.as_string()
    context = ssl.create_default_context()

    try:
        with smtplib.SMTP_SSL(
            host=settings.SMTP_HOST, 
            port=settings.SMTP_PORT, 
            context=context,
            timeout=30
        ) as server:
            server.ehlo()
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.sendmail(settings.SMTP_USER, contact, msg_)
            response = "200"

    except smtplib.SMTPConnectError as exc:
        response = str(exc)
    except smtplib.SMTPTimeoutError as exc: 
        response = str(exc)
        raise self.retry(exc=exc, countdown=60, max_retries=3)
    except smtplib.SMTPRecipientsRefused as exc:
        response = str(exc)
    except smtplib.SMTPServerDisconnected as exc:
        response = str(exc)
    except smtplib.SMTPAuthenticationError as exc:
        response = str(exc)

    finally:
        obj = NotificationLogAddDTO(receiver=contact, message=msg,response=response)
        asyncio.run(insert_result_into_database(obj))
    