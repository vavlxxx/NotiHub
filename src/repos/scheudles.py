from datetime import datetime, timezone
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from src.repos.base import BaseRepository
from src.schemas.notifications import ScheduleDTO, ScheduleWithChannelsDTO
from src.models.notifications import NotificationSchedule


class ScheduleRepository(BaseRepository):
    schema = ScheduleDTO
    model = NotificationSchedule

    async def get_current_schedules_to_perform(self, *filter, **filter_by) -> list[ScheduleWithChannelsDTO]:
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
    