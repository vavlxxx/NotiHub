from datetime import datetime

from src.schemas.base import BaseDTO


class NotificationLogAddDTO(BaseDTO):
    receiver: str
    message: str
    response: str

class NotificationLogDTO(NotificationLogAddDTO):
    id: int
    sent_at : datetime

class NotificationSendDTO(BaseDTO):
    template_id: int
    channels_ids: list[int]
    variables: dict[str, str]
