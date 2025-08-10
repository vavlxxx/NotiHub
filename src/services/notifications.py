from jinja2 import TemplateSyntaxError, meta

from src.utils.enums import ContactChannelType
from src.schemas.notifications import NotificationSendDTO
from src.services.base import BaseService
from src.settings import settings
from src.tasks.tasks import send_telegram_notification, send_email_notification
from src.utils.exceptions import (
    ChannelNotFoundError,
    MissingTemplateVariablesError,
    ObjectNotFoundError, 
    TemplateNotFoundError,
    TemplateSyntaxCheckError
)

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
            raise MissingTemplateVariablesError(
                detail=f"Отсутствуют переменная(ые): {', '.join(sorted(missing_variables))}"
            )
        
        try:
            return settings.JINGA2_ENV.from_string(template.content).render(**template_variables)
        except TemplateSyntaxError as exc:
            raise TemplateSyntaxCheckError from exc


    async def send_notification(self, data: NotificationSendDTO, user_meta: dict) -> dict:
        msg = await self._validate_and_get_rendered_template(
            template_id=data.template_id, 
            template_variables=data.variables
        )
        channels = await self.db.channels.get_all_filtered_by_ids(
            ids_list=data.channels_ids, 
            is_active=True, 
            user_id=user_meta.get("user_id")
        )
        channels_ids = [channel.id for channel in channels]
        if len(channels_ids) != len(data.channels_ids):
            raise ChannelNotFoundError(
                detail=f"Не удалось найти у Вас активный(ые) канал(ы) с id: {', '.join(map(str, set(data.channels_ids) - set(channels_ids)))}"
            )

        for channel in channels:
            if channel.channel_type == ContactChannelType.EMAIL:
                send_email_notification.delay(contact=channel.contact_value, msg=msg)
            if channel.channel_type == ContactChannelType.TELEGRAM:
                send_telegram_notification.delay(contact=channel.contact_value, msg=msg)
