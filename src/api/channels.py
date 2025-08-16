from pathlib import Path
from fastapi import APIRouter, Body, Depends

from api.examples.channels import EXAMPLE_CHANNELS
from src.schemas.channels import RequestAddChannelDTO, UpdateChannelDTO
from src.dependencies.users import auth_required, UserMetaDep
from src.dependencies.db import DBDep
from src.services.channels import ChannelService

from src.utils.exceptions import (
    ChannelExistsError, 
    ChannelExistsHTTPError,
    ChannelInUseError,
    ChannelInUseHTTPError, 
    ChannelNotFoundError,
    ChannelNotFoundHTTPError
)


router = APIRouter(
    prefix="/channels",
    tags=["Управление контактными каналами пользователей"],
    dependencies=[Depends(auth_required)]
)


@router.post("/", summary="Добавить канал")
async def add_channel(
    db: DBDep,
    user_meta: UserMetaDep,
    data: RequestAddChannelDTO = Body(description="Данные о контактном канале", openapi_examples=EXAMPLE_CHANNELS)
):  
    try:
        channel = await ChannelService(db).add_channel(data=data, user_meta=user_meta)
    except ChannelExistsError as exc:
        raise ChannelExistsHTTPError from exc
    return {
        "data": channel
    }


@router.patch("/{channel_id}", summary="Обновить канал")
async def update_channel(
    db: DBDep,
    user_meta: UserMetaDep,
    data: UpdateChannelDTO = Body(description="Данные о контактном канале", openapi_examples=EXAMPLE_CHANNELS),
    channel_id: int = Path(description="ID канала") # type: ignore
):
    try:
        await ChannelService(db).update_channel(data=data, channel_id=channel_id, user_meta=user_meta)
    except ChannelNotFoundError as exc:
        raise ChannelNotFoundHTTPError from exc
    except ChannelExistsError as exc:
        raise ChannelExistsHTTPError from exc
    except ChannelInUseError as exc:
        raise ChannelInUseHTTPError(detail=exc.detail) from exc
    return {
        "status": "OK"
    }


@router.delete("/{channel_id}", summary="Удалить канал")
async def delete_channel(
    db: DBDep,
    user_meta: UserMetaDep,
    channel_id: int = Path(description="ID канала") # type: ignore
):
    try:
        await ChannelService(db).delete_channel(channel_id=channel_id, user_meta=user_meta)
    except ChannelNotFoundError as exc:
        raise ChannelNotFoundHTTPError from exc
    except ChannelInUseError as exc:
        raise ChannelInUseHTTPError(detail=exc.detail) from exc
    return {
        "status": "OK"
    }
