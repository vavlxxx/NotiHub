from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import ENUM
from sqlalchemy.orm import mapped_column, Mapped, relationship

from src.models.base import Base
from src.utils.enums import ContactChannelType, UserRole


class User(Base):
    first_name: Mapped[str | None]
    last_name: Mapped[str | None]
    role: Mapped[UserRole] = mapped_column(
        ENUM(UserRole), 
        nullable=False,
        server_default=UserRole.USER
    )
    username: Mapped[str] = mapped_column(unique=True)
    password_hash: Mapped[str]
    notification_enabled: Mapped[bool] = mapped_column(default=True)
    contact_channels: Mapped[list["UserContactChannel"]] = relationship(
        back_populates="user"
    )

    __tablename__ = "users"


class UserContactChannel(Base):
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    contact_value: Mapped[str]
    is_active: Mapped[bool] = mapped_column(default=True)
    user: Mapped["User"] = relationship(
        back_populates="contact_channels",
    )
    channel_type: Mapped[ContactChannelType] = mapped_column(
        ENUM(ContactChannelType), 
        nullable=False
    )

    __tablename__ = "user_contact_channels"
    __table_args__ = (
        UniqueConstraint(
            "user_id", 
            "channel_type", 
            "contact_value", 
            name='unique_user_channel_contact'
        ),
    )
