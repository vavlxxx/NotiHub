from datetime import datetime

from sqlalchemy import DateTime, func
from sqlalchemy.orm import Mapped, mapped_column

from src.models.base import Base


class NotificationLog(Base):
    receiver: Mapped[str]
    response: Mapped[str]
    message: Mapped[str]
    sent_at : Mapped[datetime] = mapped_column(DateTime(timezone=True), default= func.now(), server_default=func.now())

    __tablename__ = "notification_logs"
    