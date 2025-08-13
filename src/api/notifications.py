from fastapi import APIRouter, Body, Depends

from src.schemas.notifications import NotificationMassSendDTO, NotificationSendDTO
from src.dependencies.db import DBDep
from src.dependencies.users import auth_required, UserMetaDep, only_staff
from src.services.notifications import NotificationService
from src.api.examples.notifications import EXAMPLE_NOTIFICATIONS
from src.utils.exceptions import (
    ChannelNotFoundError,
    ChannelNotFoundHTTPError,
    MissingTemplateVariablesError,
    MissingTemplateVariablesHTTPError,
    TemplateNotFoundError,
    TemplateNotFoundHTTPError,
)


router = APIRouter(
    prefix="/notifications",
    tags=["Управление уведомлениями"],
    dependencies=[Depends(auth_required)]
)


@router.post("/sendOne", summary="Отправить уведомление")
async def send_one_notification(
    db: DBDep,
    user_meta: UserMetaDep,
    data: NotificationSendDTO = Body(description="Параметры уведомеления", openapi_examples=EXAMPLE_NOTIFICATIONS),
):  
    try:
        response = await NotificationService(db).send_notifications(
            data=data, 
            user_meta=user_meta
        )
    except TemplateNotFoundError as exc:
        raise TemplateNotFoundHTTPError from exc
    except MissingTemplateVariablesError as exc:
        raise MissingTemplateVariablesHTTPError(detail=exc.detail) from exc
    except ChannelNotFoundError as exc:
        raise ChannelNotFoundHTTPError(detail=exc.detail) from exc
    return {
        "status": "OK",
        "data": response
    }


@router.post("/sendMany", summary="Массовая рассылка всем пользователям", dependencies=[Depends(only_staff)])
async def send_many_notifications(
    db: DBDep,
    user_meta: UserMetaDep,
    data: NotificationMassSendDTO,
):
    try:
        response = await NotificationService(db).send_notifications(
            data=data, 
            user_meta=user_meta
        )
    except TemplateNotFoundError as exc:
        raise TemplateNotFoundHTTPError from exc
    except MissingTemplateVariablesError as exc:
        raise MissingTemplateVariablesHTTPError(detail=exc.detail) from exc
    return {
        "status": "OK",
        "data": response
    }

# @router.get("/getReport", summary="Получить отчет по статистике уведомлений", dependencies=[Depends(only_staff)])
# async def get_report(
#     db: DBDep,
#     user_meta: UserMetaDep,
# ):  
#     response = await NotificationService(db).get_report()
#     return {
#         "status": "OK",
#         "data": response
#     }


# @router.get("/getSchedule", summary="Получить расписание уведомлений")
# async def get_schedule(
#     db: DBDep,
#     user_meta: UserMetaDep,
# ):  
#     response = await NotificationService(db).get_schedule(
#         user_meta=user_meta
#     )
#     return {
#         "status": "OK",
#         "data": response
#     }