from datetime import datetime
import typing

from sqlalchemy import DateTime, ForeignKey, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base


if typing.TYPE_CHECKING:
    from src.models.users import UserContactChannel


class Notification(Base):
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    template_id: Mapped[int] = mapped_column(ForeignKey("templates.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default= func.now(), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default= func.now(), onupdate=func.now())
    
    channels: Mapped[list["UserContactChannel"]] = relationship(
        secondary="notification_channels",
        back_populates="notifications",
    )
    variables: Mapped[list["NotificationVariable"]] = relationship(
        back_populates="notification",
        cascade="all, delete-orphan"
    )

    __tablename__ = "notifications"
    __table_args__ = (
        UniqueConstraint("user_id", "template_id", name="unique_user_template"),
    )


class NotificationChannel(Base):
    notification_id: Mapped[int] = mapped_column(ForeignKey("notifications.id", ondelete="CASCADE"))
    channel_id: Mapped[int] = mapped_column(ForeignKey("user_contact_channels.id", ondelete="CASCADE"))

    __tablename__ = "notification_channels"


class NotificationVariable(Base):
    key: Mapped[str]
    value: Mapped[str]
    notification_id: Mapped[int] = mapped_column(ForeignKey("notifications.id", ondelete="CASCADE"))
    notification: Mapped["Notification"] = relationship(back_populates="variables")

    __tablename__ = "notification_variables"


class NotificationLog(Base):
    receiver: Mapped[str]
    response: Mapped[str]
    sended_message: Mapped[str]
    sent_at : Mapped[datetime] = mapped_column(DateTime(timezone=True), default= func.now(), server_default=func.now())

    __tablename__ = "notification_logs"
    