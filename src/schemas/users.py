from pydantic import Field

from src.schemas.channels import UserChannelDTO
from src.schemas.base import BaseDTO
from src.utils.enums import UserRole


class _UserDTO(BaseDTO):
    first_name: str | None = None
    last_name: str | None  = None
    notification_enabled: bool = True

class UserLoginRequestDTO(BaseDTO):
    username: str
    password: str = Field(..., min_length=8)

class UserRegisterRequestDTO(UserLoginRequestDTO):
    role: UserRole = UserRole.USER

class UserRegisterDTO(BaseDTO):
    username: str
    password_hash: str
    role: UserRole = UserRole.USER

class UserDTO(_UserDTO):
    id: int
    username: str
    role: UserRole
    
class UserWithChannelsDTO(UserDTO):
    channels: list[UserChannelDTO] | None = Field(default_factory=list)

class UserPasswdDTO(UserDTO):
    password_hash: str

class UserUpdateDTO(_UserDTO):
    ...
