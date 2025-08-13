import asyncio
import logging
from datetime import datetime, timezone

from croniter import croniter

from src.tasks.extras import CELERY_TASKS
from src.tasks.app import celery_app
from src.utils.db_manager import DB_Manager
from src.db import sessionmaker_null_pool
from src.utils.enums import ScheduleType

from src.schemas.notifications import (
    RequestAddLogDTO, 
    UpdateScheduleDTO, 
    ScheduleWithChannelsDTO
)


logger = logging.getLogger("src.tasks.beat")


@celery_app.task(name="check_notification_schedule")
def check_notification_schedule():
    asyncio.run(_process_scheduled_notifications())


async def _process_scheduled_notifications():
    async with DB_Manager(session_factory=sessionmaker_null_pool) as db:
        schedules = await db.schedules.get_current_schedules_to_perform()
        for schedule in schedules:
            logger.info("Got schedule to handle: %s", schedule)
            CELERY_TASKS[schedule.channel.channel_type].delay(
                RequestAddLogDTO(
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
    
    if schedule.max_executions == 0 or (new_executions_count >= schedule.max_executions):
        await db.schedules.delete(ensure_existence=False, id=schedule.id)
        logger.info("Reached 'max_executions': (%d) count, schedule was deleted: %s", schedule.max_executions, schedule)
        return
    
    if schedule.schedule_type == ScheduleType.RECURRING and schedule.crontab:
        now = datetime.now(timezone.utc)
        cron = croniter(schedule.crontab, now)
        next_execution_time = cron.get_next(datetime)
        logger.info("New 'next execution' time for RECURRING schedule: %s", next_execution_time)

    await db.schedules.edit(
        ensure_existence=False,
        id=schedule.id, 
        data=UpdateScheduleDTO(
            current_executions=new_executions_count,
            last_executed_at=datetime.now(timezone.utc),
            next_execution_at=next_execution_time
        )
    )
