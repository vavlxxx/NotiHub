from datetime import datetime

from pydantic import Field, FutureDatetime, field_validator

from src.schemas.channels import UserChannelDTO
from src.schemas.base import BaseDTO
from src.utils.enums import (
    ContactChannelType, 
    NotificationStatus,
    ScheduleType
)


class NotificationLogSendDTO(BaseDTO):
    message: str
    contact_data: str
    provider_name: ContactChannelType


class NotificationLogAddDTO(NotificationLogSendDTO):
    status: NotificationStatus = NotificationStatus.PENDING
    processing_time_ms: int = 0

class NotificationLogDTO(NotificationLogAddDTO):
    id: int
    delivered_at : datetime
    provider_response: str | None


class _NotificationSchedule(BaseDTO):
    schedule_type: ScheduleType = ScheduleType.ONCE
    scheduled_at: FutureDatetime | None = None
    crontab: str | None = None
    max_executions: int | None = Field(None, gt=0)

    @field_validator('max_executions', mode='before')
    @classmethod
    def validate_once_scheduled_at(cls, v, values):
        if values.data.get('schedule_type') == ScheduleType.ONCE and v:
            raise ValueError("max_executions makes no sense for 'ONCE' notifications")
        return v

    @field_validator('crontab', mode='before')
    @classmethod
    def validate_recurring_cron(cls, v, values):
        if values.data.get('schedule_type') == ScheduleType.ONCE and v:
            raise ValueError("crontab makes no sense for 'ONCE' notifications")
        
        elif values.data.get('schedule_type') == ScheduleType.RECURRING and not v:
            raise ValueError("crontab is required for 'RECURRING' notifications")
        if v:
            try:
                from croniter import croniter
                croniter(v)
            except ValueError:
                raise ValueError("Invalid crontab expression")
        return v


class NotificationSendDTO(_NotificationSchedule):
    template_id: int
    channels_ids: list[int]
    variables: dict[str, str]


class NotificationScheduleAddDTO(_NotificationSchedule):
    message: str
    channel_id: int
    scheduled_at: datetime | None = None
    next_execution_at: datetime | None = None
    

class NotificationScheduleDTO(NotificationScheduleAddDTO):
    id: int
    created_at: datetime
    updated_at: datetime
    last_executed_at: datetime | None = None
    current_executions: int

class NotificationScheduleUpdateDTO(BaseDTO):
    last_executed_at: datetime | None = None
    next_execution_at: datetime | None = None
    current_executions: int


class ScheduleWithChannelsDTO(NotificationScheduleDTO):
    channel: UserChannelDTO
    