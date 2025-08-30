from datetime import datetime
from typing import Sequence

from sqlalchemy import desc, func, select, text, update, insert
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.exc import DBAPIError
from asyncpg import DataError

from src.schemas.base import BaseDTO
from src.repos.base import BaseRepository
from src.schemas.notifications import LogDTO, RequestAddLogDTO
from src.models.notifications import NotificationLog
from src.utils.enums import NotificationStatus
from src.utils.exceptions import ValueOutOfRangeError


class NotificationLogRepository(BaseRepository):
    model = NotificationLog
    schema = LogDTO

    async def get_all_filtered_by_date(self, date_begin: datetime, date_end: datetime):
        query = select(self.model).filter(
            self.model.delivered_at.between(date_begin, date_end)
        )  # type: ignore
        result = await self.session.execute(query)
        return [self.schema.model_validate(obj) for obj in result.scalars().all()]

    async def add_or_edit(self, data: RequestAddLogDTO, **params) -> int:
        query = select(self.model).filter_by(
            **data.model_dump(exclude={"status"}), status=NotificationStatus.PENDING
        )

        result = await self.session.execute(query)
        obj = result.scalar_one_or_none()
        notification_id = obj.id if obj else None

        if notification_id is None:
            add_obj_stmt = (
                insert(self.model)
                .values(**data.model_dump(), **params)
                .returning(self.model.id)
            )
            result = await self.session.execute(add_obj_stmt)
            notification_id = result.scalars().one()
        else:
            upd = (
                update(self.model)
                .where(self.model.id == notification_id)
                .values(status=data.status, **params)
            )
            await self.session.execute(upd)
        return notification_id

    async def get_history_with_pagination(
        self,
        limit: int,
        offset: int,
        user_id: int | None,
        date_begin: datetime | None = None,
        date_end: datetime | None = None,
    ) -> tuple[int, list[LogDTO]]:
        query_total_count = (
            select(func.count()).select_from(self.model).filter_by(sender_id=user_id)
        )
        query = (
            select(self.model, query_total_count.scalar_subquery().label("total_count"))
            .order_by(self.model.id.asc())
            .filter_by(sender_id=user_id)
            .order_by(desc(self.model.created_at))
        )

        if date_begin and date_end:
            query_total_count = query_total_count.filter(
                self.model.created_at.between(date_begin, date_end)
            )  # type: ignore
            query = query.filter(self.model.created_at.between(date_begin, date_end))  # type: ignore

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
        logs: list[LogDTO] = [self.schema.model_validate(row[0]) for row in rows]
        return total_count, logs

    async def add_bulk(self, data: Sequence[BaseDTO]) -> Sequence[int]:
        add_obj_stmt = pg_insert(self.model).values(
            [item.model_dump() for item in data]
        )
        add_obj_stmt = add_obj_stmt.on_conflict_do_nothing(
            index_elements=[
                "sender_id",
                "contact_data",
                "message",
                "provider_name",
            ],
            index_where=text("status = 'PENDING'"),
        )
        add_obj_stmt = add_obj_stmt.returning(self.model.id)
        result = await self.session.execute(add_obj_stmt)
        return result.scalars().all()
