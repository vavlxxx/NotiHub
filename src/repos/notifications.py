from datetime import datetime
from sqlalchemy import select

from src.repos.base import BaseRepository
from src.schemas.notifications import LogDTO
from src.models.notifications import NotificationLog


class NotificationLogRepository(BaseRepository):
    model = NotificationLog
    schema = LogDTO

    async def get_all_filtered_by_date(self, date_begin: datetime, date_end: datetime):
        query = select(self.model).filter(
            self.model.delivered_at.between(date_begin, date_end)
        )  # type: ignore
        result = await self.session.execute(query)
        return [self.schema.model_validate(obj) for obj in result.scalars().all()]
