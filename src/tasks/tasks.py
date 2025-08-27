import re
import asyncio
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


def detect_content_type(text: str) -> ContentType:
    if not text:
        return ContentType.PLAIN

    html_tags = re.findall(r"<[^>]+>", text)
    if html_tags:
        valid_html_pattern = r"<(?:/?[a-zA-Z][a-zA-Z0-9]*(?:\s[^>]*)?|!--.*?--)>"
        if re.search(valid_html_pattern, text, re.DOTALL | re.IGNORECASE):
            return ContentType.HTML

    return ContentType.PLAIN


class NotificationLogger:
    def __init__(
        self,
        log_schema: RequestAddLogDTO,
    ):
        self.log_schema = log_schema

    async def _insert_result_into_database(self, data: AddLogDTO):
        async with DB_Manager(session_factory=sessionmaker_null_pool) as db:
            await db.notification_logs.add(data)
            await db.commit()

    async def log_result(
        self,
        status: NotificationStatus = NotificationStatus.FAILURE,
        details: str | None = None,
    ):
        new_log_schema = AddLogDTO(
            **self.log_schema.model_dump(),
            details=details,
            status=status,
        )
        logger.info("New log, after sending notification: %s", new_log_schema)
        await self._insert_result_into_database(new_log_schema)


logger = logging.getLogger("src.tasks.tasks")


@celery_app.task(name="send_to_telegram")
def send_telegram_notification(log_data: dict):
    log_schema = RequestAddLogDTO(**log_data)
    asyncio.run(send_telegram_message(log_schema))


async def send_telegram_message(
    log_schema: RequestAddLogDTO,
    status: NotificationStatus = NotificationStatus.FAILURE,
    details: str | None = None,
):
    bot_message_method_url = (
        settings.TELEGRAM_BOT_API_URL.format(settings.TELEGRAM_BOT_TOKEN)
        + "/sendMessage"
    )
    body = {"chat_id": log_schema.contact_data, "text": log_schema.message}

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(url=bot_message_method_url, json=body) as response:
                if response.status == 200:
                    status = NotificationStatus.SUCCESS
                    logger.info(
                        "Successfully sent telegram message to: %s",
                        log_schema.contact_data,
                    )
                    return

                data = await response.json()
                details = data.get("description")
                logger.warning(
                    "Failure during sending telegram message to: %s, response: %s",
                    log_schema.contact_data,
                    details,
                )
                raise Exception(details)

    except Exception as exc:
        details = f"Unexpected Error: {str(exc)}"
        logger.error("Unexpected error during telegram notification sending: %s", exc)
        raise exc

    finally:
        await NotificationLogger(log_schema).log_result(status=status, details=details)


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
        port=settings.SMTP_PORT,
    )
    return response


@celery_app.task(name="send_to_email", default_retry_delay=10, max_retries=3)
def send_email_notification(log_data: dict):
    log_schema = RequestAddLogDTO(**log_data)
    asyncio.run(send_email(log_schema))


async def send_email(
    log_schema: RequestAddLogDTO,
    status: NotificationStatus = NotificationStatus.FAILURE,
    details: str | None = None,
):
    try:
        asyncio.run(_send_email_message(log_schema))
        logger.info("Successfully sent email message to: %s", log_schema.contact_data)
        status = NotificationStatus.SUCCESS

    except aiosmtplib.SMTPAuthenticationError as exc:
        details = f"Auth Error: {exc}"
        logger.error("Failed authentication to SMTP server: %s", exc)

    except aiosmtplib.SMTPRecipientsRefused as exc:
        details = f"Recipients Refused: {exc}"
        logger.error("Failed to send email to recipients: %s", exc)

    except aiosmtplib.SMTPConnectError as exc:
        details = f"SMTP Connect Error: {exc}"
        logger.error("Failed to connect to the SMTP server: %s", exc)

    except aiosmtplib.SMTPServerDisconnected as exc:
        details = f"Server Disconnected: {exc}"
        logger.error("Server disconnected: %s", exc)

    except TimeoutError as exc:
        details = f"Timeout Error: {exc}"
        logger.error("Time for connection is out: %s", exc)

    except ConnectionAbortedError as exc:
        details = f"Connection Aborted: {exc}"
        logger.error("Connection to SMTP was aborted: %s", exc)

    except Exception as exc:
        details = f"Unexpected Error: {exc}"
        logger.error("Unexpected error during email sending: %s", exc)
        raise

    await NotificationLogger(log_schema).log_result(status=status, details=details)


@celery_app.task(name="send_push")
def send_push_notification(log_data: dict):
    log_schema = RequestAddLogDTO(**log_data)
    asyncio.run(send_push(log_schema))


async def send_push(
    log_schema: RequestAddLogDTO,
    status: NotificationStatus = NotificationStatus.FAILURE,
    details: str | None = None,
):
    ntfy_url_with_topic = settings.NTFY_API_URL + f"{log_schema.contact_data}"
    headers = {"Title": settings.APP_NAME, "Content-Type": "text/plain; charset=utf-8"}

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                url=ntfy_url_with_topic,
                data=log_schema.message.encode("utf-8"),
                headers=headers,
            ) as response:
                if response.status == 200:
                    status = NotificationStatus.SUCCESS
                    logger.info(
                        "Successfully sent push notification to topic: %s",
                        log_schema.contact_data,
                    )
                    await response.json()
                    return

                logger.warning(
                    "Failure during sending telegram message to: %s",
                    ntfy_url_with_topic,
                )

    except Exception as exc:
        details = f"Unexpected Error: {str(exc)}"
        logger.error("Unexpected error during email sending: %s", exc)
        raise exc

    finally:
        await NotificationLogger(log_schema).log_result(status=status, details=details)
