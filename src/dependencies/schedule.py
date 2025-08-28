from datetime import datetime, timedelta
from typing import Annotated

from fastapi import Depends, Query

from src.schemas.base import BaseDTO
from utils.exceptions import InvalidDatetimeRangeHTTPError


class ScheduleFiltrationDTO(BaseDTO):
    date_begin: datetime | None
    date_end: datetime | None


def get_schedule_filtration_params(
    date_begin: Annotated[
        datetime | None,
        Query(description="Начало промежутка оповещения", examples=[datetime.now()]),
    ] = None,
    date_end: Annotated[
        datetime | None,
        Query(
            description="Конец промежутка оповещения",
            examples=([datetime.now() + timedelta(days=1)]),
        ),
    ] = None,
) -> ScheduleFiltrationDTO:
    if date_begin is not None and date_end is not None and date_begin > date_end:
        raise InvalidDatetimeRangeHTTPError
    return ScheduleFiltrationDTO(date_begin=date_begin, date_end=date_end)


ScheduleFiltrationDep = Annotated[
    ScheduleFiltrationDTO, Depends(get_schedule_filtration_params)
]
