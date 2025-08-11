import ssl
import smtplib
import asyncio
import aiohttp
from time import perf_counter
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timezone

from src.tasks.app import celery_app
from src.settings import settings
from src.utils.db_manager import DB_Manager
from src.db import sessionmaker_null_pool
from src.utils.enums import ContactChannelType, NotificationStatus
from src.utils.enums import ScheduleType
from src.schemas.notifications import (
    NotificationLogAddDTO, 
    NotificationLogSendDTO,
    NotificationScheduleUpdateDTO, 
    ScheduleWithChannelsDTO
)


async def insert_result_into_database(data: NotificationLogAddDTO):
    async with DB_Manager(session_factory=sessionmaker_null_pool) as db:
        await db.notification_logs.add(data)
        await db.commit()


async def send_telegram_message(log_schema: NotificationLogAddDTO):
    status = NotificationStatus.FAILURE
    start = perf_counter()
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                url=f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}/sendMessage", 
                json={
                    "chat_id": log_schema.contact_data, 
                    "text": log_schema.message
                }
            ):
                status = NotificationStatus.SUCCESS
    finally:
        end = perf_counter()
        log_schema.processing_time_ms = int((end - start) * 1000)
        log_schema.status = status
        await insert_result_into_database(log_schema)


@celery_app.task(name="send_to_telegram")
def send_telegram_notification(log_data: dict):
    log_schema = NotificationLogAddDTO(**log_data)
    asyncio.run(send_telegram_message(log_schema))


@celery_app.task(name="send_to_email")
def send_email_notification(log_data: dict):
    log_schema = NotificationLogAddDTO(**log_data)
    start = perf_counter()
    message = MIMEMultipart("alternative")
    message["Subject"] = "🔔 NotiHub | Уведомление"
    message["From"] = settings.SMTP_USER
    message["To"] = log_schema.contact_data
    message.attach(MIMEText(log_schema.message, "plain"))
    msg_ = message.as_string()

    context = ssl.create_default_context()
    status = NotificationStatus.FAILURE

    try:
        with smtplib.SMTP_SSL(
            host=settings.SMTP_HOST, 
            port=settings.SMTP_PORT, 
            context=context
        ) as server:
            server.ehlo()
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.sendmail(settings.SMTP_USER, log_schema.contact_data, msg_)
            status = NotificationStatus.SUCCESS

    except smtplib.SMTPConnectError:
        ...
    except smtplib.SMTPRecipientsRefused:
        ...
    except smtplib.SMTPServerDisconnected:
        ...
    except smtplib.SMTPAuthenticationError:
        ...
    except ConnectionAbortedError:
        ...

    finally:
        end = perf_counter()
        log_schema.processing_time_ms = int((end - start) * 1000)
        log_schema.status = status
        asyncio.run(insert_result_into_database(log_schema))


@celery_app.task(name="check_notification_schedule")
def check_notification_schedule():
    asyncio.run(_process_scheduled_notifications())


async def _process_scheduled_notifications():
    async with DB_Manager(session_factory=sessionmaker_null_pool) as db:
        schedules = await db.schedules.get_current_schedules_to_perform()
        for schedule in schedules:
            CELERY_TASKS = {
                ContactChannelType.EMAIL: send_email_notification,
                ContactChannelType.TELEGRAM: send_telegram_notification
            }

            CELERY_TASKS[schedule.channel.channel_type].delay(
                NotificationLogSendDTO(
                    message=schedule.message,
                    contact_data=schedule.channel.contact_value,
                    provider_name=schedule.channel.channel_type
                ).model_dump()
            )
            await _update_schedule_after_execution(db, schedule)

        await db.commit()


async def _update_schedule_after_execution(db: DB_Manager, schedule: ScheduleWithChannelsDTO):
    next_execution_time = schedule.scheduled_at
    new_executions_count = schedule.current_executions + 1
    
    if schedule.schedule_type == ScheduleType.RECURRING and schedule.crontab:
        from croniter import croniter
        now = datetime.now(timezone.utc)
        cron = croniter(schedule.crontab, now)
        next_execution_time = cron.get_next(datetime)
        
        if schedule.max_executions and new_executions_count >= schedule.max_executions:
            await db.schedules.delete(ensure_existence=False, id=schedule.id)
            return
    elif schedule.schedule_type == ScheduleType.ONCE and new_executions_count >= 1:
        await db.schedules.delete(ensure_existence=False, id=schedule.id)
        return

    obj = NotificationScheduleUpdateDTO(
        current_executions=new_executions_count,
        last_executed_at=datetime.now(timezone.utc),
        next_execution_at=next_execution_time
    )
    await db.schedules.edit(id=schedule.id, data=obj)
