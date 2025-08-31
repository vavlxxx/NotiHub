import asyncio
import aiohttp
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

import aiosmtplib

from src.tasks.app import celery_app
from src.settings import settings
from src.utils.enums import ContentType, NotificationStatus
from src.schemas.notifications import RequestAddLogDTO
from src.utils.notification_helper import NotificationHelper as NH
from src.utils.exceptions import ForbiddenHTMLTemplateError


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
        if NH.detect_content_type(log_schema.message) == ContentType.HTML:
            raise ForbiddenHTMLTemplateError

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

    except ForbiddenHTMLTemplateError:
        details = "HTML templates are not supported for Telegram notifications"
        logger.error(details)
    except Exception as exc:
        details = f"Unexpected Error: {str(exc)}"
        logger.error("Unexpected error during telegram notification sending: %s", exc)
        raise exc

    finally:
        await NH(log_schema).log_result(status=status, details=details)


async def _send_email_message(log_schema: RequestAddLogDTO):
    message = MIMEMultipart("alternative")
    message["Subject"] = settings.APP_NAME
    message["From"] = settings.SMTP_USER
    message["To"] = log_schema.contact_data

    content_type = NH.detect_content_type(log_schema.message)
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


@celery_app.task(
    bind=True,
    max_retries=3,
    name="send_to_email",
    default_retry_delay=10,
)
def send_email_notification(self, log_data: dict):
    log_schema = RequestAddLogDTO(**log_data)
    asyncio.run(send_email(self, log_schema))


async def send_email(
    self,
    log_schema: RequestAddLogDTO,
    status: NotificationStatus = NotificationStatus.FAILURE,
    details: str | None = None,
):
    try:
        await _send_email_message(log_schema)
        logger.info("Successfully sent email message to: %s", log_schema.contact_data)
        status = NotificationStatus.SUCCESS

    except aiosmtplib.SMTPAuthenticationError as exc:
        details = f"Auth Error: {exc}"
        logger.error("Failed authentication to SMTP server: %s", exc)
        raise self.retry(exc=exc, countdown=self.request.retries * 2)

    except aiosmtplib.SMTPRecipientsRefused as exc:
        details = f"Recipients Refused: {exc}"
        logger.error("Failed to send email to recipients: %s", exc)
        raise self.retry(exc=exc, countdown=self.request.retries * 2)

    except aiosmtplib.SMTPConnectError as exc:
        details = f"SMTP Connect Error: {exc}"
        logger.error("Failed to connect to the SMTP server: %s", exc)
        raise self.retry(exc=exc, countdown=self.request.retries * 2)

    except aiosmtplib.SMTPServerDisconnected as exc:
        details = f"Server Disconnected: {exc}"
        logger.error("Server disconnected: %s", exc)
        raise self.retry(exc=exc, countdown=self.request.retries * 2)

    except TimeoutError as exc:
        details = f"Timeout Error: {exc}"
        logger.error("Time for connection is out: %s", exc)
        raise self.retry(exc=exc, countdown=self.request.retries * 2)

    except ConnectionAbortedError as exc:
        details = f"Connection Aborted: {exc}"
        logger.error("Connection to SMTP was aborted: %s", exc)
        raise self.retry(exc=exc, countdown=self.request.retries * 2)

    except Exception as exc:
        details = f"Unexpected Error: {exc}"
        logger.error("Unexpected error during email sending: %s", exc)
        raise

    await NH(log_schema).log_result(status=status, details=details)


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
        if NH.detect_content_type(log_schema.message) == ContentType.HTML:
            raise ForbiddenHTMLTemplateError

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

    except ForbiddenHTMLTemplateError:
        details = "HTML templates are not supported for Push notifications"
        logger.error(details)
    except Exception as exc:
        details = f"Unexpected Error: {str(exc)}"
        logger.error("Unexpected error during email sending: %s", exc)
        raise exc

    finally:
        await NH(log_schema).log_result(status=status, details=details)


# @celery_app.task(name="send_sms")
# def send_sms_notification(log_data: dict):
#     log_schema = RequestAddLogDTO(**log_data)
#     asyncio.run(send_sms(log_schema))


# async def send_sms(
#     log_schema: RequestAddLogDTO,
#     status: NotificationStatus = NotificationStatus.FAILURE,
#     details: str | None = None,
# ):
#     method_url = settings.SMSRU_SEND_METHOD
#     params = {
#         "api_id": settings.SMSRU_API_KEY,
#         "to": log_schema.contact_data,
#         "msg": log_schema.message,
#         "json": 1,
#     }

#     try:
#         if NH.detect_content_type(log_schema.message) == ContentType.HTML:
#             raise ForbiddenHTMLTemplateError

#         async with aiohttp.ClientSession() as session:
#             async with session.post(
#                 url=method_url,
#                 params=params,
#             ) as response:
#                 data = await response.json()
#                 print("DATA", data)
#                 if response.status == 200 and data.get("status") == "OK":
#                     status = NotificationStatus.SUCCESS
#                     logger.info(
#                         "Successfully sent SMS to: %s",
#                         log_schema.contact_data,
#                     )
#                     return

#                 data = await response.json()
#                 details = data.get("status_text", "Unknown error")
#                 logger.warning(
#                     "Failure during sending SMS to: %s, response: %s",
#                     log_schema.contact_data,
#                     details,
#                 )

#     except ForbiddenHTMLTemplateError:
#         details = "HTML templates are not supported for SMS notifications"
#         logger.error(details)
#     except Exception as exc:
#         details = f"Unexpected Error: {str(exc)}"
#         logger.error("Unexpected error during SMS sending: %s", exc)
#         raise exc

#     finally:
#         await NH(log_schema).log_result(status=status, details=details)
