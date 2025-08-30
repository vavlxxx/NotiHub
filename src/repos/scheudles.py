from datetime import datetime, timezone
from typing import Sequence

from sqlalchemy import CursorResult, delete, desc, func, select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm import joinedload
from asyncpg import DataError

from src.schemas.base import BaseDTO
from src.repos.base import BaseRepository
from src.schemas.notifications import ScheduleDTO, ScheduleWithChannelsDTO
from src.models.notifications import NotificationSchedule
from src.models.users import UserContactChannel
from src.utils.exceptions import ObjectNotFoundError, ValueOutOfRangeError


class ScheduleRepository(BaseRepository):
    schema = ScheduleDTO
    model = NotificationSchedule

    async def add_bulk(self, data: Sequence[BaseDTO]):
        add_obj_stmt = pg_insert(self.model).values(
            [item.model_dump() for item in data]
        )
        excluded = add_obj_stmt.excluded
        add_obj_stmt = add_obj_stmt.on_conflict_do_update(
            constraint="unique_schedules",
            set_={
                "updated_at": func.now(),
                "next_execution_at": func.GREATEST(
                    excluded.next_execution_at,
                    NotificationSchedule.next_execution_at,
                ),
            },
        )
        add_obj_stmt = add_obj_stmt.returning(self.model.id)
        result = await self.session.execute(add_obj_stmt)
        return result.scalars().all()

    async def get_current_schedules_to_perform(
        self, *filter, **filter_by
    ) -> list[ScheduleWithChannelsDTO]:
        query = (
            select(self.model)
            .filter(
                NotificationSchedule.next_execution_at <= datetime.now(timezone.utc),
                *filter,
            )
            .filter_by(**filter_by)
            .options(joinedload(NotificationSchedule.channel))
        )
        result = await self.session.execute(query)
        return [
            ScheduleWithChannelsDTO.model_validate(obj)
            for obj in result.scalars().all()
        ]

    async def get_all_nearest_with_pagination(
        self,
        limit: int,
        offset: int,
        user_id: int,
        date_begin: datetime | None = None,
        date_end: datetime | None = None,
    ) -> tuple[int, list[ScheduleDTO]]:
        query_total_count = (
            select(func.count())
            .select_from(self.model)
            .outerjoin(
                UserContactChannel, self.model.channel_id == UserContactChannel.id
            )  # type: ignore
            .filter_by(user_id=user_id)
        )
        query = (
            select(self.model, query_total_count.scalar_subquery().label("total_count"))
            .order_by(self.model.id.asc())
            .outerjoin(
                UserContactChannel, self.model.channel_id == UserContactChannel.id
            )  # type: ignore
            .filter_by(user_id=user_id)
            .order_by(desc(self.model.next_execution_at))
        )

        if date_begin and date_end:
            query_total_count = query_total_count.filter(
                self.model.next_execution_at.between(date_begin, date_end)
            )  # type: ignore
            query = query.filter(
                self.model.next_execution_at.between(date_begin, date_end)
            )  # type: ignore

        query = query.limit(limit).offset(offset)

        try:
            result = await self.session.execute(query)
        except DBAPIError as exc:
            if isinstance(exc.orig.__cause__, DataError):  # type: ignore
                raise ValueOutOfRangeError(detail=exc.orig.__cause__.args[0]) from exc  # type: ignore
            raise exc
        rows = result.fetchall()

        if not rows:
            total_count_result = await self.session.execute(query_total_count)
            total_count = total_count_result.scalar() or 0
            return total_count, []

        total_count = rows[0].total_count
        scheudles: list[ScheduleDTO] = [
            self.schema.model_validate(row[0]) for row in rows
        ]
        return total_count, scheudles

    async def delete_by_user(self, schedule_id: int, user_id: int):
        query_channels_ids_by_user = (
            select(UserContactChannel.id)
            .filter_by(user_id=user_id)
            .subquery(name="get_channels_by_user")
        )
        delete_obj_stmt = (
            delete(self.model)
            .filter(self.model.channel_id.in_(select(query_channels_ids_by_user)))  # type: ignore
            .filter_by(id=schedule_id)
        )

        try:
            result: CursorResult = await self.session.execute(delete_obj_stmt)
        except DBAPIError as exc:
            if isinstance(exc.orig.__cause__, DataError):  # type: ignore
                raise ValueOutOfRangeError(detail=exc.orig.__cause__.args[0]) from exc  # type: ignore
            raise exc

        if result.rowcount == 0:
            raise ObjectNotFoundError
