from src.repos.base import BaseRepository
from src.schemas.notifications import NotificationLogDTO
from src.models.notifications import NotificationLog



class NotificationLogRepository(BaseRepository):
    model = NotificationLog
    schema = NotificationLogDTO

