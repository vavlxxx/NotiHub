from datetime import datetime

from pydantic import Field, field_validator

from src.schemas.channels import UserChannelDTO
from src.schemas.base import BaseDTO


class _NotificationDTO(BaseDTO):
    template_id: int

class NotificationAddRequestDTO(_NotificationDTO):
    channels_ids: list[int] | None = Field(default_factory=list)
    variables: dict[str, str]

class NotificationAddDTO(_NotificationDTO):
    user_id: int

class NotificationUpdateDTO(_NotificationDTO):
    template_id: int | None = None
    channels_ids: list[int] | None = Field(default_factory=list)
    variables: dict[str, str] | None = None


class NotificationChannelAddDTO(BaseDTO):
    channel_id: int
    notification_id: int

class NotificationChannelDTO(NotificationChannelAddDTO):
    id: int

class NotificationVariableDTO(BaseDTO):
    key: str
    value: str

class NotificationVariableAddDTO(NotificationVariableDTO):
    notification_id: int

class NotificationDTO(_NotificationDTO):
    id: int
    created_at: datetime
    updated_at: datetime

class NotificationWithRelsDTO(NotificationDTO):
    channels: list[UserChannelDTO]
    variables: dict[str, str]

    @field_validator('variables', mode='before')
    @classmethod
    def shrink_variables(cls, v) -> dict[str, str]:
        if isinstance(v, list):
            return {var.key: var.value for var in v}
        return v

class NotificationLogDTO(NotificationAddRequestDTO):
    receiver: str
    sended_message: str
    response: str
    sent_at : datetime
