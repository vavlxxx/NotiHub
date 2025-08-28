from pydantic import Field, model_validator

from src.schemas.channels import ChannelDTO
from src.schemas.base import BaseDTO
from src.utils.enums import UserRole


class _UserDTO(BaseDTO):
    first_name: str | None = None
    last_name: str | None = None


class RequestLoginUserDTO(BaseDTO):
    username: str
    password: str = Field(..., min_length=8)


class RequestRegisterUserDTO(RequestLoginUserDTO):
    role: UserRole = UserRole.USER


class RegisterUserDTO(BaseDTO):
    username: str
    password_hash: str
    role: UserRole = UserRole.USER


class UserDTO(_UserDTO):
    id: int
    username: str
    role: UserRole


class UserWithChannelsDTO(UserDTO):
    channels: list[ChannelDTO] | None = Field(default_factory=list)


class UserWithPasswordDTO(UserDTO):
    password_hash: str


class UserUpdateDTO(_UserDTO):
    @model_validator(mode="after")
    def validate_all_fields_are_providen(self):
        values = tuple(self.model_dump().values())
        if all(map(lambda val: val is None, values)):
            raise ValueError("provide at least one non-empty field")
        return self
