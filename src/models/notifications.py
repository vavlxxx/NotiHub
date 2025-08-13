import typing
from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.utils.enums import NotificationStatus, ContactChannelType, ScheduleType
from src.models.base import Base

if typing.TYPE_CHECKING:
    from src.models.users import UserContactChannel


class NotificationLog(Base):
    contact_data: Mapped[str]
    message: Mapped[str] = mapped_column(
        Text, nullable=False
    )
    provider_name: Mapped[ContactChannelType] = mapped_column(
        ENUM(ContactChannelType), nullable=False
    )
    provider_response: Mapped[str | None] = mapped_column(
        String(), nullable=True, comment="Ответ от провайдера"
    )
    status: Mapped[NotificationStatus] = mapped_column(
        ENUM(NotificationStatus), nullable=False
    )
    delivered_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=func.now(), server_default=func.now()
    )

    __tablename__ = "notification_logs"


class NotificationSchedule(Base):
    message: Mapped[str] = mapped_column(
        Text, nullable=False
    )
    channel_id: Mapped[int] = mapped_column(
        ForeignKey("user_contact_channels.id", onupdate="restrict", ondelete="restrict")
    )
    schedule_type: Mapped[ScheduleType] = mapped_column(
        String(20), 
        nullable=False,
        default=ScheduleType.ONCE
    )
    scheduled_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), 
        nullable=True
    )
    crontab: Mapped[str | None] = mapped_column(
        String(100), 
        nullable=True,
        comment="Cron выражение: минута час день месяц день_недели"
    )
    max_executions: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        comment="Максимальное количество выполнений"
    )
    current_executions: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        comment="Текущее количество выполнений"
    )
    last_executed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True
    )
    next_execution_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Следующее время выполнения (вычисляется автоматически)"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        default=func.now(), 
        server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=func.now(),
        onupdate=func.now()
    )
    channel: Mapped["UserContactChannel"] = relationship(
        "UserContactChannel",
        back_populates="schedules"
    )

    __tablename__ = "notification_schedules"
    
    __table_args__ = (
        CheckConstraint(
            "(max_executions >= 0) AND (current_executions <= max_executions) AND (current_executions >= 0)",
            name='valid_execution_count'
        ),
        CheckConstraint(
            "(schedule_type = 'ONCE' AND scheduled_at IS NOT NULL) OR schedule_type != 'ONCE'",
            name='once_requires_scheduled_at'
        ),
        CheckConstraint(
            "(schedule_type = 'RECURRING' AND crontab IS NOT NULL) OR schedule_type != 'RECURRING'",
            name='recurring_requires_cron'
        )
    )
