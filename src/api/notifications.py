import math

from fastapi import APIRouter, Body, Depends, Path
from fastapi_cache.decorator import cache

from src.api.texts.notifications import (
    API_DESCR_NOTIFICATIONS_SENDALL,
    API_DESCR_NOTIFICATIONS_SENDONE,
    DESCR_API_GET_REPORT,
    DESCR_API_GET_SCHEDULES,
    DESCR_API_GET_HISTORY,
)
from src.api.examples.notifications import (
    EXAMPLE_NOTIFICATIONS,
    EXAMPLE_NOTIFICATIONS_FOR_ALL,
)

from src.schemas.notifications import NotificationMassSendDTO, NotificationSendDTO
from src.dependencies.db import DBDep
from src.dependencies.users import auth_required, UserMetaDep, only_staff
from src.dependencies.pagination import PaginationDep
from src.dependencies.schedule import ScheduleFiltrationDep
from src.services.notifications import NotificationService

from src.utils.exceptions import (
    ChannelNotFoundError,
    ChannelNotFoundHTTPError,
    ForbiddenHTMLTemplateError,
    ForbiddenHTMLTemplateHTTPError,
    MissingTemplateVariablesError,
    MissingTemplateVariablesHTTPError,
    NotificationExistsError,
    NotificationExistsHTTPError,
    ScheduleAlreadyExistsError,
    ScheduleAlreadyExistsHTTPError,
    ScheduleNotFoundError,
    ScheduleNotFoundHTTPError,
    TemplateNotFoundError,
    TemplateNotFoundHTTPError,
    ValueOutOfRangeError,
    ValueOutOfRangeHTTPError,
)


router = APIRouter(
    prefix="/notifications",
    tags=["Управление уведомлениями"],
    dependencies=[Depends(auth_required)],
)


@router.post(
    "/sendOne",
    summary="Отправить уведомление",
    description=API_DESCR_NOTIFICATIONS_SENDONE,
)
async def send_one_notification(
    db: DBDep,
    user_meta: UserMetaDep,
    data: NotificationSendDTO = Body(
        description="Параметры уведомеления", openapi_examples=EXAMPLE_NOTIFICATIONS
    ),
):
    try:
        response = await NotificationService(db).send_notifications(
            data=data, user_meta=user_meta
        )
    except ScheduleAlreadyExistsError as exc:
        raise ScheduleAlreadyExistsHTTPError from exc
    except ValueOutOfRangeError as exc:
        raise ValueOutOfRangeHTTPError(detail=exc.detail) from exc
    except NotificationExistsError as exc:
        raise NotificationExistsHTTPError from exc
    except TemplateNotFoundError as exc:
        raise TemplateNotFoundHTTPError from exc
    except MissingTemplateVariablesError as exc:
        raise MissingTemplateVariablesHTTPError(detail=exc.detail) from exc
    except ForbiddenHTMLTemplateError as exc:
        raise ForbiddenHTMLTemplateHTTPError(detail=exc.detail) from exc
    except ChannelNotFoundError as exc:
        raise ChannelNotFoundHTTPError(detail=exc.detail) from exc
    return {"status": "OK", "data": response}


@router.post(
    "/sendMany",
    summary="Массовая рассылка всем пользователям | Только для персонала",
    dependencies=[Depends(only_staff)],
    description=API_DESCR_NOTIFICATIONS_SENDALL,
)
async def send_many_notifications(
    db: DBDep,
    user_meta: UserMetaDep,
    data: NotificationMassSendDTO = Body(
        description="Параметры уведомеления",
        openapi_examples=EXAMPLE_NOTIFICATIONS_FOR_ALL,
    ),
):
    try:
        response = await NotificationService(db).send_notifications(
            data=data, user_meta=user_meta
        )
    except ScheduleAlreadyExistsError as exc:
        raise ScheduleAlreadyExistsHTTPError from exc
    except NotificationExistsError as exc:
        raise NotificationExistsHTTPError from exc
    except ValueOutOfRangeError as exc:
        raise ValueOutOfRangeHTTPError(detail=exc.detail) from exc
    except TemplateNotFoundError as exc:
        raise TemplateNotFoundHTTPError from exc
    except ForbiddenHTMLTemplateError as exc:
        raise ForbiddenHTMLTemplateHTTPError(detail=exc.detail) from exc
    except MissingTemplateVariablesError as exc:
        raise MissingTemplateVariablesHTTPError(detail=exc.detail) from exc
    return {"status": "OK", "data": response}


@cache(expire=120)
@router.get(
    "/getSchedules",
    summary="Получить расписание уведомлений",
    description=DESCR_API_GET_SCHEDULES,
)
async def get_schedules_list(
    db: DBDep,
    user_meta: UserMetaDep,
    pagination: PaginationDep,
    filtration: ScheduleFiltrationDep,
):
    try:
        total_count, response = await NotificationService(db).get_schedules(
            user_meta=user_meta,
            limit=pagination.limit,
            offset=pagination.offset,
            date_begin=filtration.date_begin,
            date_end=filtration.date_end,
        )
    except ValueOutOfRangeError as exc:
        raise ValueOutOfRangeHTTPError(detail=exc.detail) from exc

    resp = {
        "status": "OK",
        "page": pagination.page,
        "per_page": pagination.limit,
        "total_count": total_count,
        "total_pages": math.ceil(total_count / pagination.limit),
        "data": response,
    }

    if filtration.date_begin and filtration.date_end:
        resp["period"] = (
            {"period_start": filtration.date_begin, "period_end": filtration.date_end},
        )
    return resp


@cache(expire=120)
@router.get(
    "/getHistory",
    summary="Получить историю отправленных уведомлений",
    description=DESCR_API_GET_HISTORY,
)
async def get_notifications_history(
    db: DBDep,
    user_meta: UserMetaDep,
    pagination: PaginationDep,
    filtration: ScheduleFiltrationDep,
):
    try:
        total_count, response = await NotificationService(db).get_history(
            user_meta=user_meta,
            limit=pagination.limit,
            offset=pagination.offset,
            date_begin=filtration.date_begin,
            date_end=filtration.date_end,
        )
    except ValueOutOfRangeError as exc:
        raise ValueOutOfRangeHTTPError(detail=exc.detail) from exc

    resp = {
        "status": "OK",
        "page": pagination.page,
        "per_page": pagination.limit,
        "total_count": total_count,
        "total_pages": math.ceil(total_count / pagination.limit),
        "data": response,
    }

    if filtration.date_begin and filtration.date_end:
        resp["period"] = (
            {"period_start": filtration.date_begin, "period_end": filtration.date_end},
        )
    return resp


@router.delete(
    "/deleteSchedule/{schedule_id}",
    summary="Удалить расписание уведомлений",
    dependencies=[Depends(auth_required)],
)
async def delete_schedule(
    db: DBDep,
    user_meta: UserMetaDep,
    schedule_id: int = Path(description="ID расписания"),
):
    try:
        await NotificationService(db).delete_schedule(
            schedule_id=schedule_id, user_meta=user_meta
        )
    except ScheduleNotFoundError as exc:
        raise ScheduleNotFoundHTTPError from exc
    except ValueOutOfRangeError as exc:
        raise ValueOutOfRangeHTTPError(detail=exc.detail) from exc

    return {"status": "OK"}


@router.get(
    "/getReport",
    summary="Получить отчет по статистике уведомлений | Только для персонала",
    dependencies=[Depends(only_staff)],
    description=DESCR_API_GET_REPORT,
)
async def get_report(db: DBDep, filtration: ScheduleFiltrationDep):
    response = await NotificationService(db).get_report(
        date_begin=filtration.date_begin, date_end=filtration.date_end
    )
    return {"status": "OK", "data": response}
