from enum import Enum

from pydantic import Field

from src.schemas.base import BaseDTO


class ContactChannelType(str, Enum):
    EMAIL = "Почта"
    TELEGRAM = "Telegram"


class UserChannelAddDTO(BaseDTO):
    user_id: int
    contact_value: str
    channel_type: ContactChannelType
    
class UserChannelDTO(UserChannelAddDTO):
    id: int
    is_active: bool


class _UserDTO(BaseDTO):
    first_name: str | None
    last_name: str | None
    notification_enabled: bool | None

class UserRegisterRequestDTO(BaseDTO):
    username: str | None
    password: str = Field(..., min_length=8)

class UserLoginRequestDTO(UserRegisterRequestDTO): ...


class UserRegisterDTO(BaseDTO):
    username: str
    password_hash: str

class UserDTO(_UserDTO):
    id: int
    username: str
    
class UserWithChannelsDTO(UserDTO):
    contact_channels: list[UserChannelDTO]

class UserPasswdDTO(UserDTO):
    password_hash: str

class UserUpdateDTO(_UserDTO):
    ...
