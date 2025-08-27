from datetime import datetime

from croniter import croniter
from pydantic import Field, FutureDatetime, model_validator

from src.schemas.channels import ChannelDTO
from src.schemas.base import BaseDTO
from src.utils.enums import ContactChannelType, NotificationStatus, ScheduleType


class RequestAddLogDTO(BaseDTO):
    message: str
    contact_data: str
    provider_name: ContactChannelType


class AddLogDTO(RequestAddLogDTO):
    status: NotificationStatus = NotificationStatus.FAILURE
    details: str | None = None


class LogDTO(AddLogDTO):
    id: int
    delivered_at: datetime


class _ScheduleDTO(BaseDTO):
    schedule_type: ScheduleType = ScheduleType.ONCE
    scheduled_at: FutureDatetime | None = None
    crontab: str | None = None
    max_executions: int = Field(default=0, ge=0)

    @model_validator(mode="after")
    def validate_schedule_fields(self) -> "_ScheduleDTO":
        if self.schedule_type == ScheduleType.ONCE:
            if self.max_executions > 0:
                raise ValueError(
                    "'max_executions' makes no sense for 'ONCE' notifications"
                )
            if self.crontab:
                raise ValueError("crontab makes no sense for 'ONCE' notifications")

        elif self.schedule_type == ScheduleType.RECURRING:
            if self.max_executions < 0:
                raise ValueError(
                    "'max_executions' must be greater than 0 for 'RECURRING' notifications"
                )
            if not self.crontab:
                raise ValueError("crontab is required for 'RECURRING' notifications")

            if self.crontab:
                try:
                    croniter(self.crontab)
                except ValueError:
                    raise ValueError("Invalid crontab expression")
        return self


class NotificationMassSendDTO(_ScheduleDTO):
    template_id: int
    variables: dict[str, str]


class NotificationSendDTO(NotificationMassSendDTO):
    channels_ids: list[int]


class AddScheduleDTO(_ScheduleDTO):
    message: str
    channel_id: int
    scheduled_at: datetime | None = None
    next_execution_at: datetime | None = None


class ScheduleDTO(AddScheduleDTO):
    id: int
    created_at: datetime
    updated_at: datetime
    last_executed_at: datetime | None = None
    current_executions: int


class UpdateScheduleDTO(BaseDTO):
    last_executed_at: datetime | None = None
    next_execution_at: datetime | None = None
    current_executions: int


class ScheduleWithChannelsDTO(ScheduleDTO):
    channel: ChannelDTO
