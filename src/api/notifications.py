from fastapi import APIRouter, Depends, Path

from src.dependencies.db import DBDep
from src.dependencies.users import auth_required, UserMetaDep
from src.dependencies.templates import PaginationDep
from src.services.notifications import NotificationService
from src.schemas.notifications import NotificationUpdateDTO, NotificationAddRequestDTO
from src.utils.exceptions import (
    ChannelNotFoundError, 
    ChannelNotFoundHTTPError,
    MissingTemplateVariablesError,
    MissingTemplateVariablesHTTPError, 
    NotificationExistsError, 
    NotificationExistsHTTPError, 
    NotificationNotFoundError, 
    NotificationNotFoundHTTPError,
    TemplateNotFoundError,
    TemplateNotFoundHTTPError
)


router = APIRouter(
    prefix="/notifications",
    tags=["Управление уведомлениями"],
    dependencies=[Depends(auth_required)]
)


@router.get("/", summary="Получить список уведомлений аутентифицированного пользователя")
async def get_notifications_list(
    db: DBDep,
    user_meta: UserMetaDep,
    pagination: PaginationDep
):
    notifications = await NotificationService(db).get_notifications_list(
        user_meta=user_meta,
        limit=pagination.limit,
        offset=pagination.offset
    )
    return {
        "page": pagination.page,
        "offset": pagination.offset,
        "data": notifications
    }


@router.post("/send/{notification_id}", summary="Отправить уведомление")
async def send_notification(
    db: DBDep,
    user_meta: UserMetaDep,
    notification_id: int = Path(description="ID уведомления"),
):  
    try:
        response = await NotificationService(db).send_notification(user_meta=user_meta, notification_id=notification_id)
    except NotificationNotFoundError as exc:
        raise NotificationNotFoundHTTPError from exc
    return {
        "status": "OK",
        "data": response
    }


@router.post("/", summary="Создать уведомление")
async def add_notification(
    db: DBDep,
    user_meta: UserMetaDep,
    data: NotificationAddRequestDTO
):  
    try:
        await NotificationService(db).create_notification(data=data, user_meta=user_meta)
    except TemplateNotFoundError as exc:
        raise TemplateNotFoundHTTPError from exc
    except NotificationExistsError as exc:
        raise NotificationExistsHTTPError from exc
    except MissingTemplateVariablesError as exc:
        raise MissingTemplateVariablesHTTPError(detail=exc.detail) from exc
    except ChannelNotFoundError as exc:
        raise ChannelNotFoundHTTPError(detail=exc.detail) from exc
    return (
        {"status": "OK"}
)


@router.patch("/{notification_id}", summary="Обновить уведомление")
async def update_notification(
    db: DBDep,
    user_meta: UserMetaDep,
    data: NotificationUpdateDTO,
    notification_id: int = Path(description="ID уведомления"),
):  
    try:
        await NotificationService(db).update_notification(
            data=data,
            user_meta=user_meta,
            notification_id=notification_id
        )
    except NotificationNotFoundError as exc:
        raise NotificationNotFoundHTTPError from exc
    except NotificationExistsError as exc:
        raise NotificationExistsHTTPError from exc
    except ChannelNotFoundError as exc:
        raise ChannelNotFoundHTTPError from exc
    return (
        {"status": "OK"}
)


@router.delete("/{notification_id}", summary="Удалить уведомление")
async def delete_notification(
    db: DBDep,
    user_meta: UserMetaDep,
    notification_id: int = Path(description="ID уведомления")
):
    try:
        await NotificationService(db).delete_notification(user_meta=user_meta, notification_id=notification_id)
    except NotificationNotFoundError as exc:
        raise NotificationNotFoundHTTPError from exc
    return { "status": "OK" }
