import asyncio
import re
import aiohttp
import logging

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

import aiosmtplib

from src.tasks.app import celery_app
from src.settings import settings
from src.utils.db_manager import DB_Manager
from src.db import sessionmaker_null_pool
from src.utils.enums import ContentType, NotificationStatus
from src.schemas.notifications import AddLogDTO, RequestAddLogDTO


logger = logging.getLogger("src.tasks.tasks")


async def insert_result_into_database(data: AddLogDTO):
    async with DB_Manager(session_factory=sessionmaker_null_pool) as db:
        await db.notification_logs.add(data)
        await db.commit()


@celery_app.task(name="send_to_telegram")
def send_telegram_notification(log_data: dict):
    log_schema = RequestAddLogDTO(**log_data)
    asyncio.run(send_telegram_message(log_schema))


async def send_telegram_message(log_schema: RequestAddLogDTO):
    status = NotificationStatus.FAILURE
    provider_response = None
    bot_message_method_url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage"
    body = { "chat_id": log_schema.contact_data, "text": log_schema.message }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url=bot_message_method_url, json=body) as response:
                if response.status == 200:
                    status = NotificationStatus.SUCCESS
                    logger.info("Successfully sent telegram message to: %s", log_schema.contact_data)
                    return
                
                data = await response.json()
                provider_response = data.get("description")
                logger.warning(
                    "Failure during sending telegram message to: %s, response: %s", 
                    log_schema.contact_data, 
                    provider_response
                )
    except Exception as exc:
        provider_response = f"Unexpected Error: {str(exc)}"
        logger.error("Unexpected error during email sending: %s", exc)
        raise exc
    
    finally:
        new_log_schema = AddLogDTO(
            **log_schema.model_dump(),
            provider_response=provider_response,
            status=status,
        )
        logger.info("New log, after sending notification: %s", new_log_schema)
        await insert_result_into_database(new_log_schema)


def detect_content_type(content: str) -> str:
    html_indicators = [
        '<html', '<body', '<div', '<p>', '<br', '<table', 
        '<h1', '<h2', '<h3', '<strong', '<em', '<a href'
    ]
    
    content_lower = content.lower()
    if any(tag in content_lower for tag in html_indicators):
        return ContentType.HTML
    if re.search(r'<[^>]+>', content):
        return ContentType.HTML
    
    return ContentType.PLAIN


async def _send_email_message(log_schema: RequestAddLogDTO):
    message = MIMEMultipart("alternative")
    message["Subject"] = settings.APP_NAME
    message["From"] = settings.SMTP_USER
    message["To"] = log_schema.contact_data
    
    content_type = detect_content_type(log_schema.message)
    message.attach(MIMEText(log_schema.message, ContentType.PLAIN.value))
    if content_type == ContentType.HTML:
        message.attach(MIMEText(log_schema.message, ContentType.HTML.value))

    msg_ = message.as_string()

    response = await aiosmtplib.send(
        msg_,
        sender=settings.SMTP_USER,
        recipients=[log_schema.contact_data],
        username=settings.SMTP_USER,
        password=settings.SMTP_PASSWORD,
        use_tls=True,
        hostname=settings.SMTP_HOST, 
        port=settings.SMTP_PORT
    )
    return response
        

@celery_app.task(bind=True, name="send_to_email", default_retry_delay=10, max_retries=3)
def send_email_notification(self, log_data: dict):
    log_schema = RequestAddLogDTO(**log_data)
    status = NotificationStatus.FAILURE
    provider_response = None
    should_retry = False
    exc = None

    try:
        asyncio.run(_send_email_message(log_schema))        
        logger.info("Successfully sent email message to: %s", log_schema.contact_data)
        status = NotificationStatus.SUCCESS

    except aiosmtplib.SMTPConnectError as exc:
        provider_response = f"SMTP Connect Error: {str(exc)}"
        logger.error("Failed to connect to the SMTP server: %s", exc)
        
    except aiosmtplib.SMTPRecipientsRefused as exc:
        provider_response = f"Recipients Refused: {str(exc)}"
        logger.error("Failed to send email to recipients: %s", exc)
        
    except aiosmtplib.SMTPAuthenticationError as exc:
        provider_response = f"Auth Error: {str(exc)}"
        logger.error("Failed authentication to SMTP server: %s", exc)
        
    except aiosmtplib.SMTPServerDisconnected as exc:
        provider_response = f"Server Disconnected: {str(exc)}"
        logger.error("Server disconnected: %s", exc)
        should_retry = True
        
    except TimeoutError as exc:
        provider_response = f"Timeout Error: {str(exc)}"
        logger.error("Time for connection is out: %s", exc)
        should_retry = True

    except ConnectionAbortedError as exc:
        provider_response = f"Connection Aborted: {str(exc)}"
        logger.error("Connection to SMTP was aborted: %s", exc)
        should_retry = True
        
    except Exception as exc:
        provider_response = f"Unexpected Error: {str(exc)}"
        logger.error("Unexpected error during email sending: %s", exc)
        raise exc

    if should_retry:
        if self.request.retries < self.max_retries:
            logger.info("Retrying email send to %s in %s seconds", log_schema.contact_data, self.default_retry_delay)
            raise self.retry(exc=exc, countdown=self.default_retry_delay)
        
        logger.error("Max retries exceeded for email to %s", log_schema.contact_data)
        status = NotificationStatus.FAILURE

    new_log_schema = AddLogDTO(
        **log_schema.model_dump(),
        provider_response=provider_response,
        status=status,
    )
    logger.info("New log, after sending notification: %s", new_log_schema)
    asyncio.run(insert_result_into_database(new_log_schema))
