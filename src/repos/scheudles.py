from datetime import datetime, timezone
from sqlalchemy import select
from sqlalchemy.orm import joinedload, selectinload

from src.repos.base import BaseRepository
from src.schemas.notifications import NotificationScheduleDTO, ScheduleWithChannelsDTO
from src.models.notifications import NotificationSchedule
from src.models.users import UserContactChannel


class ScheduleRepository(BaseRepository):
    schema = NotificationScheduleDTO
    model = NotificationSchedule

    async def get_current_schedules_to_perform(self, *filter, **filter_by) -> list[NotificationScheduleDTO]:
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
    