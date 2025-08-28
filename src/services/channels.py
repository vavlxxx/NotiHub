from collections import ChainMap
from typing import Any

from pydantic import ValidationError

from src.services.base import BaseService
from src.schemas.channels import (
    AddChannelDTO,
    RequestAddChannelDTO,
    ChannelDTO,
    UpdateChannelDTO,
)
from src.utils.exceptions import (
    ChannelInUseError,
    ChannelValidationError,
    ObjectExistsError,
    ObjectNotFoundError,
    ChannelExistsError,
    ChannelNotFoundError,
)


class ChannelService(BaseService):
    async def add_channel(
        self, data: RequestAddChannelDTO, user_meta: dict
    ) -> ChannelDTO:
        new_data = AddChannelDTO(
            **data.model_dump(), user_id=user_meta.get("user_id", 0)
        )
        try:
            channel: ChannelDTO = await self.db.channels.add(new_data)
        except ObjectExistsError as exc:
            raise ChannelExistsError from exc

        await self.db.commit()
        return channel

    async def update_channel(
        self, data: UpdateChannelDTO, channel_id: int, user_meta: dict
    ) -> ChannelDTO:
        schedules: list[ChannelDTO] = await self.db.schedules.get_all_filtered(
            channel_id=channel_id
        )
        if schedules:
            raise ChannelInUseError(
                detail="Данный канал используется в запланированных уведомлениях с id: "
                + ", ".join(map(str, [schedule.id for schedule in schedules]))
            )

        try:
            channel_before_update: ChannelDTO = await self.db.channels.get_one(
                id=channel_id, user_id=user_meta.get("user_id", 0)
            )
            data_before_update: dict[str, Any] = channel_before_update.model_dump(
                exclude={"user_id"}
            )
            RequestAddChannelDTO(**ChainMap(data.model_dump(), data_before_update))
        except ObjectNotFoundError as exc:
            raise ChannelNotFoundError from exc
        except ValidationError as exc:
            raise ChannelValidationError from exc

        try:
            channel: ChannelDTO = await self.db.channels.edit(
                data=data,
                id=channel_id,
                user_id=user_meta.get("user_id", 0),
                ensure_existence=False,
            )
        except ObjectExistsError as exc:
            raise ChannelExistsError from exc

        await self.db.commit()
        return channel

    async def delete_channel(self, channel_id: int, user_meta: dict) -> None:
        schedules: list[ChannelDTO] = await self.db.schedules.get_all_filtered(
            channel_id=channel_id
        )
        if schedules:
            raise ChannelInUseError(
                detail="Данный канал используется в запланированных уведомлениях с id: "
                + ", ".join(map(str, [schedule.id for schedule in schedules]))
            )

        try:
            await self.db.channels.delete(
                id=channel_id, user_id=user_meta.get("user_id", 0)
            )
        except ObjectNotFoundError as exc:
            raise ChannelNotFoundError from exc
        await self.db.commit()
