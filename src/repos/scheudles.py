from datetime import datetime, timezone

from sqlalchemy import CursorResult, delete, func, select
from sqlalchemy.orm import joinedload

from src.repos.base import BaseRepository
from src.schemas.notifications import ScheduleDTO, ScheduleWithChannelsDTO
from src.models.notifications import NotificationSchedule
from src.models.users import UserContactChannel
from src.utils.exceptions import ObjectNotFoundError


class ScheduleRepository(BaseRepository):
    schema = ScheduleDTO
    model = NotificationSchedule

    async def get_current_schedules_to_perform(self, ckeck_next_execution=True, *filter, **filter_by) -> list[ScheduleWithChannelsDTO]:
        query = (
            select(self.model)
            .filter(
                NotificationSchedule.next_execution_at <= datetime.now(timezone.utc), 
                *filter
            )
            .filter_by(**filter_by)
            .options(joinedload(NotificationSchedule.channel))
        )
        result = await self.session.execute(query)
        return [ScheduleWithChannelsDTO.model_validate(obj) for obj in result.scalars().all()]
    

    async def get_all_nearest_with_pagination(
            self, 
            limit: int, 
            offset: int, 
            user_id: int | None,
            date_begin: datetime | None = None,
            date_end: datetime | None = None,
        ) -> tuple[int, list[ScheduleDTO]]:

        query_total_count = (
            select(func.count())
            .select_from(self.model)
            .outerjoin(UserContactChannel, self.model.channel_id == UserContactChannel.id) # type: ignore
            .filter_by(user_id=user_id)
        )
        query = (
            select(self.model, query_total_count.scalar_subquery().label("total_count"))
            .order_by(self.model.id.asc())
            .outerjoin(UserContactChannel, self.model.channel_id == UserContactChannel.id) # type: ignore
            .filter_by(user_id=user_id)
        )

        if date_begin and date_end:
            query_total_count = query_total_count.filter(self.model.next_execution_at.between(date_begin, date_end)) # type: ignore
            query = query.filter(self.model.next_execution_at.between(date_begin, date_end)) # type: ignore

        query = query.limit(limit).offset(offset) 
        result = await self.session.execute(query)
        rows = result.fetchall()

        if not rows:
            total_count_result = await self.session.execute(query_total_count)
            total_count = total_count_result.scalar() or 0
            return total_count, []

        total_count = rows[0].total_count
        templates: list[ScheduleDTO] = [self.schema.model_validate(row[0]) for row in rows]
        return total_count, templates
    

    async def delete_by_user(self, schedule_id: int, user_id: int):
        query_channels_ids_by_user = (
            select(UserContactChannel.id)
            .filter_by(user_id=user_id)
            .subquery(name="get_channels_by_user")
        )
        delete_obj_stmt = (
            delete(self.model)
            .filter(self.model.channel_id.in_(select(query_channels_ids_by_user))) # type: ignore
            .filter_by(id=schedule_id)
        )
        result: CursorResult = await self.session.execute(delete_obj_stmt)
        if result.rowcount == 0:
            raise ObjectNotFoundError
        