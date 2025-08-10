from fastapi import APIRouter, Depends

from src.schemas.notifications import NotificationSendDTO
from src.dependencies.db import DBDep
from src.dependencies.users import auth_required, UserMetaDep
from src.services.notifications import NotificationService
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


@router.post("/", summary="Отправить уведомление")
async def send_notification(
    db: DBDep,
    user_meta: UserMetaDep,
    data: NotificationSendDTO,
):  
    try:
        response = await NotificationService(db).send_notification(
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
