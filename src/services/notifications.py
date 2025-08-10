from jinja2 import TemplateSyntaxError, UndefinedError, meta

from src.schemas.notifications import (
    NotificationAddDTO, 
    NotificationAddRequestDTO, 
    NotificationChannelAddDTO, 
    NotificationVariableAddDTO
)
from src.services.base import BaseService
from src.settings import settings
from src.utils.exceptions import (
    ChannelNotFoundError,
    MissingTemplateVariablesError,
    NotificationNotFoundError,
    NotificationExistsError,
    ObjectExistsError,
    ObjectNotFoundError, 
    TemplateNotFoundError, 
    TemplateSyntaxCheckError
)

class NotificationService(BaseService):

    async def get_notifications_list(self, limit: int, offset: int, user_meta: dict) -> list[dict]:
        return await self.db.notifications.get_all_filtered_with_params(
            limit=limit, 
            offset=offset,
            user_id=user_meta.get('user_id')
        )

    async def _validate_and_get_template_variables(self, template_id: int, template_variables: dict) -> None:
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
                detail=f"Предоставьте переменную(ые): {', '.join(sorted(missing_variables))}"
            )
        return required_variables


    async def create_notification(self, data: NotificationAddRequestDTO, user_meta: dict) -> dict:
        required_variables = await self._validate_and_get_template_variables(
            template_id=data.template_id, 
            template_variables=data.variables
        )

        channels_ids = await self.db.channels.get_all_filtered_by_ids(ids_list=data.channels_ids)
        if len(channels_ids) != len(data.channels_ids):
            raise ChannelNotFoundError(
                detail=f"Канал(ы) с id: {', '.join(map(str, set(data.channels_ids) - set(channels_ids)))} не найдены у Вас"
            )

        _notification_data = NotificationAddDTO(
            **data.model_dump(exclude={"channels_ids", "variables"}), 
            user_id=user_meta.get("user_id")
        )
        try:
            notification = await self.db.notifications.add(_notification_data)
        except ObjectExistsError as exc:
            raise NotificationExistsError from exc

        if required_variables:
            notification_variables = [
                NotificationVariableAddDTO(
                    key=key, 
                    value=value, 
                    notification_id=notification.id
                ) for key, value in data.variables.items()
            ]
            await self.db.notification_variables.add_bulk(notification_variables)

        if data.channels_ids:
            notification_channels = [
                NotificationChannelAddDTO(
                    channel_id=channel_id, 
                    notification_id=notification.id
                ) for channel_id in data.channels_ids
            ]
            await self.db.notification_channels.add_bulk(notification_channels)

        await self.db.commit()
        return notification


    async def update_notification(self, data: dict, notification_id: int) -> dict:
        ...

    async def delete_notification(self, notification_id: int, user_meta: dict) -> None:
        try:
            await self.db.notifications.delete(id=notification_id, user_id=user_meta.get("user_id"))
        except ObjectNotFoundError as exc:
            raise NotificationNotFoundError from exc
        await self.db.commit()

    async def send_notification(self, user_meta: dict, notification_id: int) -> dict:
        ...