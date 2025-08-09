from src.schemas.channels import UserChannelAddDTO, UserChannelAddRequestDTO, UserChannelDTO, UserChannelUpdateDTO
from src.services.base import BaseService


from src.utils.exceptions import (
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
        try:
            channel = await self.db.channels.edit(data=data, id=channel_id, user_id=user_meta.get("user_id"))
        except ObjectExistsError as exc:
            raise ChannelExistsError from exc
        except ObjectNotFoundError as exc:
            raise ChannelNotFoundError from exc
        
        await self.db.commit()
        return channel

    async def delete_channel(self, channel_id: int, user_meta: dict) -> None:
        try:
            await self.db.channels.delete(id=channel_id, user_id=user_meta.get("user_id"))
        except ObjectNotFoundError as exc:
            raise ChannelNotFoundError from exc
        await self.db.commit()
        