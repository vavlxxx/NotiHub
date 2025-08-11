from datetime import datetime, timezone
from croniter import croniter
from jinja2 import TemplateSyntaxError, meta

from src.schemas.notifications import NotificationLogSendDTO, NotificationSendDTO, NotificationScheduleAddDTO
from src.services.base import BaseService
from src.settings import settings
from src.utils.enums import ContactChannelType, ScheduleType

from src.utils.exceptions import (
    ChannelNotFoundError,
    MissingTemplateVariablesError,
    ObjectNotFoundError, 
    TemplateNotFoundError,
    TemplateSyntaxCheckError
)
from tasks.tasks import send_email_notification, send_telegram_notification


class NotificationService(BaseService):

    async def _validate_and_get_rendered_template(self, template_id: int, template_variables: dict) -> None:
        try:
            template = await self.db.templates.get_one(id=template_id)
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


    async def _validate_and_get_channels(self, channels_ids: list[int], user_id: int):
        channels = await self.db.channels.get_all_filtered_by_ids(
            ids_list=channels_ids, 
            is_active=True, 
            user_id=user_id
        )
        channels_ids_ = [channel.id for channel in channels]
        if len(channels_ids_) != len(channels_ids):
            missing_channels = ', '.join(map(str, set(channels_ids) - set(channels_ids_)))
            raise ChannelNotFoundError(detail=f"У Вас отсутствуют активный(ые) канал(ы) с id: {missing_channels}")
        return channels
    
    
    def _calculate_next_execution_time(self, data: NotificationSendDTO) -> datetime:
        if data.schedule_type == ScheduleType.ONCE:
            return data.scheduled_at
        
        now = datetime.now(timezone.utc)
        start_time = data.scheduled_at or now
        
        if data.crontab:
            cron = croniter(data.crontab, start_time)
            next_time = cron.get_next(datetime)
            return next_time
        
        return None


    async def send_notification(self, data: NotificationSendDTO, user_meta: dict) -> dict:
        msg = await self._validate_and_get_rendered_template(
            template_id=data.template_id, 
            template_variables=data.variables
        )
        channels = await self._validate_and_get_channels(
            channels_ids=data.channels_ids, 
            user_id=user_meta.get("user_id")
        )
        
        
        CELERY_TASKS = {
            ContactChannelType.EMAIL: send_email_notification,
            ContactChannelType.TELEGRAM: send_telegram_notification
        }

        for channel in channels:
            if data.schedule_type == ScheduleType.ONCE and data.scheduled_at is None:
                CELERY_TASKS[channel.channel_type].delay(
                    NotificationLogSendDTO(
                        message=msg,
                        contact_data=channel.contact_value,
                        provider_name=channel.channel_type
                    ).model_dump()
                )

            else:
                next_execution_time = self._calculate_next_execution_time(data)
                scheduled_notification = NotificationScheduleAddDTO(
                    message=msg,
                    channel_id=channel.id,
                    crontab=data.crontab,
                    scheduled_at=data.scheduled_at,
                    max_executions=data.max_executions,
                    next_execution_at=next_execution_time,
                    schedule_type=data.schedule_type
                )
                await self.db.schedules.add(scheduled_notification)
            
        await self.db.commit()
        return {"message": "Уведомление отправлено"}
        