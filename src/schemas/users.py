from enum import Enum

from pydantic import Field

from src.schemas.base import BaseDTO


class ContactChannelType(str, Enum):
    EMAIL = "Почта"
    TELEGRAM = "Telegram"



class _UserDTO(BaseDTO):
    username: str | None = Field(None, min_length=8)
    first_name: str | None = Field(None)
    last_name: str | None = Field(None)

class UserRegisterDTO(BaseDTO):
    username: str = Field(..., min_length=8)
    password: str = Field(..., min_length=8)

class UserDTO(_UserDTO):
    id: int
    hashed_password: str

class UserLoginDTO(BaseDTO):
    username: str = Field(..., min_length=8)
    passwod: str = Field(..., min_length=8)

class UserUpdateDTO(_UserDTO):
    ...


