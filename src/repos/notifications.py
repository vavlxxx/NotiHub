from sqlalchemy import select
from sqlalchemy.orm import joinedload
from src.repos.base import BaseRepository
from src.schemas.notifications import (
    NotificationDTO,
    NotificationLogDTO,
    NotificationVariableAddDTO,
    NotificationWithRelsDTO,
)
from src.models.notifications import (
    Notification, 
    NotificationLog, 
    NotificationVariable
)


class NotificationRepository(BaseRepository):
    model = Notification
    schema = NotificationDTO

    async def get_all_filtered_with_params(self, limit: int, offset: int, **filter_by):
        query = (
            select(self.model)
            .filter_by(**filter_by)
            .limit(limit)
            .offset(offset)
            .options(
                joinedload(self.model.channels),
                joinedload(self.model.variables)
            )
        )
        result = await self.session.execute(query)
        return [NotificationWithRelsDTO.model_validate(obj) for obj in result.unique().scalars().all()]


class NotificationVariableRepository(BaseRepository):
    model = NotificationVariable
    schema = NotificationVariableAddDTO


class NotificationLogRepository(BaseRepository):
    model = NotificationLog
    schema = NotificationLogDTO

