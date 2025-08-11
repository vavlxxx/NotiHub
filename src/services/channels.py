from src.schemas.channels import UserChannelAddDTO, UserChannelAddRequestDTO, UserChannelDTO, UserChannelUpdateDTO
from src.services.base import BaseService


from src.utils.exceptions import (
    ChannelInUseError,
    ObjectExistsError,
    ObjectNotFoundError,
    ChannelExistsError,
    ChannelNotFoundError
)


class ChannelService(BaseService):
    
    async def add_channel(self, data: UserChannelAddRequestDTO, user_meta: dict) -> UserChannelDTO:
        new_data = UserChannelAddDTO(**data.model_dump(), user_id=user_meta.get("user_id"))
        try:
            channel = await self.db.channels.add(new_data)
        except ObjectExistsError as exc:
            raise ChannelExistsError from exc
        
        await self.db.commit()
        return channel
    
    async def update_channel(self, data: UserChannelUpdateDTO, channel_id: int, user_meta: dict) -> UserChannelDTO:
        schedules = await self.db.schedules.get_all_filtered(channel_id=channel_id)
        if schedules:
            raise ChannelInUseError(
                detail="Данный канал используется в запланированных уведомлениях с id: " + 
                ', '.join(map(str, [schedule.id for schedule in schedules]))
            )

        try:
            channel = await self.db.channels.edit(data=data, id=channel_id, user_id=user_meta.get("user_id"))
        except ObjectExistsError as exc:
            raise ChannelExistsError from exc
        except ObjectNotFoundError as exc:
            raise ChannelNotFoundError from exc
        
        await self.db.commit()
        return channel

    async def delete_channel(self, channel_id: int, user_meta: dict) -> None:
        schedules = await self.db.schedules.get_all_filtered(channel_id=channel_id)
        if schedules:
            raise ChannelInUseError(
                detail="Данный канал используется в запланированных уведомлениях с id: " + 
                ', '.join(map(str, [schedule.id for schedule in schedules]))
            )
        
        try:
            await self.db.channels.delete(id=channel_id, user_id=user_meta.get("user_id"))
        except ObjectNotFoundError as exc:
            raise ChannelNotFoundError from exc
        await self.db.commit()
        