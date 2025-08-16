import logging
from datetime import datetime, timezone
from collections import defaultdict

from croniter import croniter
from jinja2 import TemplateSyntaxError, meta
from pydantic import FutureDatetime

from schemas.channels import ChannelDTO
from schemas.templates import TemplateDTO
from src.services.base import BaseService
from src.settings import settings
from src.utils.enums import NotificationStatus, ScheduleType
from src.tasks.extras import CELERY_TASKS

from src.schemas.notifications import (
    LogDTO,
    RequestAddLogDTO,
    NotificationMassSendDTO, 
    NotificationSendDTO, 
    AddScheduleDTO,
    ScheduleDTO
)

from src.utils.exceptions import (
    ChannelNotFoundError,
    ScheduleNotFoundError,
    MissingTemplateVariablesError,
    ObjectNotFoundError, 
    TemplateNotFoundError,
    TemplateSyntaxCheckError
)


logger = logging.getLogger("src.services.notifications")


class NotificationService(BaseService):
    async def _validate_and_get_rendered_template(self, template_id: int, template_variables: dict) -> str:
        try:
            template: TemplateDTO = await self.db.templates.get_one(id=template_id)
        except ObjectNotFoundError as exc:
            raise TemplateNotFoundError from exc
        
        parsed_data = settings.JINGA2_ENV.parse(template.content)
        required_variables = meta.find_undeclared_variables(parsed_data)
        provided_variables = set(template_variables.keys())
        missing_variables = required_variables - provided_variables

        if missing_variables:
            undeclared_variables = ', '.join(sorted(missing_variables))
            raise MissingTemplateVariablesError(detail=f"Отсутствуют переменная(ые): {undeclared_variables}")
        try:
            return settings.JINGA2_ENV.from_string(template.content).render(**template_variables)
        except TemplateSyntaxError as exc:
            raise TemplateSyntaxCheckError from exc


    async def _validate_and_get_channels(self, data: NotificationSendDTO | NotificationMassSendDTO, user_meta: dict) -> list[ChannelDTO]:
        if type(data) is NotificationMassSendDTO:
            channels: list[ChannelDTO] = await self.db.channels.get_all()
            return channels

        if not isinstance(data, NotificationSendDTO):
            raise ValueError("channels_ids attribute is required")

        channels: list[ChannelDTO] = await self.db.channels.get_all_filtered_by_ids(
            ids_list=data.channels_ids,
            user_id=user_meta.get("user_id", 0)
        )
        channels_ids_ = [channel.id for channel in channels]
        if len(channels_ids_) != len(data.channels_ids):
            missing_channels = ', '.join(map(str, set(data.channels_ids) - set(channels_ids_)))
            raise ChannelNotFoundError(detail=f"У Вас отсутствуют активный(ые) канал(ы) с id: {missing_channels}")
        return channels
    
    
    def _calculate_next_execution_time(self, data: NotificationSendDTO | NotificationMassSendDTO) -> datetime | FutureDatetime | None:
        if data.schedule_type == ScheduleType.ONCE:
            return data.scheduled_at
        
        now = datetime.now(timezone.utc)
        start_time = data.scheduled_at or now
        if data.crontab:
            cron = croniter(data.crontab, start_time)
            next_time = cron.get_next(datetime)
            return next_time
        
        return None


    async def send_notifications(
            self, 
            data: NotificationSendDTO | NotificationMassSendDTO, 
            user_meta: dict
        ) -> dict[str, int]:

        msg = await self._validate_and_get_rendered_template(
            template_id=data.template_id, 
            template_variables=data.variables
        )
        channels: list[ChannelDTO] = await self._validate_and_get_channels(
            data=data,
            user_meta=user_meta
        )

        for channel in channels:
            if data.schedule_type == ScheduleType.ONCE and data.scheduled_at is None:
                ready_to_send = RequestAddLogDTO(
                    message=msg, 
                    contact_data=channel.contact_value, 
                    provider_name=channel.channel_type
                )
                logger.info("Ready to send to %s new notification: %s", channel.channel_type, ready_to_send)
                CELERY_TASKS[channel.channel_type].delay(ready_to_send.model_dump())
                continue

            scheduled_notification = AddScheduleDTO(
                message=msg,
                channel_id=channel.id,
                crontab=data.crontab,
                scheduled_at=data.scheduled_at,
                max_executions=data.max_executions,
                next_execution_at=self._calculate_next_execution_time(data),
                schedule_type=data.schedule_type
            )
            await self.db.schedules.add(scheduled_notification)
            logger.info("Prepared and scheduled for %s channel new notification: %s", channel.channel_type, scheduled_notification)

        await self.db.commit()
        return {"total_count": len(channels)}
    

    async def get_report(self, date_begin: datetime | None, date_end: datetime | None):
        report_schema = {}
        if date_begin and date_end:
            report_schema["period"] = {"period_start": date_begin, "period_end": date_end}
            notification_logs: list[LogDTO] = await self.db.notification_logs.get_all_filtered_by_date(
                date_begin=date_begin, 
                date_end=date_end
            )
        else:
            notification_logs: list[LogDTO] = await self.db.notification_logs.get_all()
        
        channels = defaultdict(lambda: {"success": 0, "failed": 0})
        for log in notification_logs:
            channel_name = getattr(log.provider_name, "value", str(log.provider_name))
            if log.status == NotificationStatus.SUCCESS:
                channels[channel_name]["success"] += 1
            elif log.status == NotificationStatus.FAILURE:
                channels[channel_name]["failed"] += 1
        
        channels_dict = {}
        for name, data in channels.items():
            total = data["success"] + data["failed"]
            channels_dict[name] = {
                **data,
                "total": total,
                "success_rate": 0 if total == 0 else round(data["success"] / total, 4)
            }
        
        report_schema["channels"] = channels_dict
        
        success_count = sum(ch["success"] for ch in channels_dict.values())
        failed_count = sum(ch["failed"] for ch in channels_dict.values())
        report_schema["summary"] = {
            "total": len(notification_logs),
            "success": success_count,
            "failed": failed_count,
            "success_rate": 0 if len(notification_logs) == 0 else round(success_count / len(notification_logs), 4)
        }
        return report_schema


    async def get_schedules(
            self, 
            limit: int, 
            offset: int, 
            user_meta: dict,
            date_begin: datetime | None,
            date_end: datetime | None
        ) -> tuple[int, list[ScheduleDTO]]:

        total_count, schedules = await self.db.schedules.get_all_nearest_with_pagination(
            user_id=user_meta.get("user_id", 0),
            limit=limit,
            offset=offset,
            date_begin=date_begin,
            date_end=date_end
        )
        return total_count, schedules


    async def delete_schedule(self, schedule_id: int, user_meta: dict) -> None:
        try:
            await self.db.schedules.delete_by_user(schedule_id=schedule_id, user_id=user_meta.get("user_id", 0))
        except ObjectNotFoundError as exc:
            raise ScheduleNotFoundError from exc
        await self.db.commit()
