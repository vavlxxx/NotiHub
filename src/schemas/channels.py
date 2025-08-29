from pydantic import EmailStr, model_validator
from pydantic import validate_email

from src.schemas.base import BaseDTO
from src.utils.enums import ContactChannelType


class RequestAddChannelDTO(BaseDTO):
    contact_value: EmailStr | str
    channel_type: ContactChannelType

    @model_validator(mode="after")
    def validate_channel_type(self):
        match self.channel_type:
            case ContactChannelType.TELEGRAM:
                if not self.contact_value.isdigit():
                    raise ValueError("telegram may be only as numeric telegram_id")
            case ContactChannelType.EMAIL:
                if not validate_email(self.contact_value):
                    raise ValueError("email must be valid string with @ and domain")
        return self


class AddChannelDTO(RequestAddChannelDTO):
    user_id: int


class ChannelDTO(BaseDTO):
    id: int
    contact_value: EmailStr | str
    channel_type: ContactChannelType


class UpdateChannelDTO(BaseDTO):
    contact_value: EmailStr | str | None = None
    channel_type: ContactChannelType | None = None

    @model_validator(mode="after")
    def validate_all_fields_are_providen(self):
        values = tuple(self.model_dump().values())
        if all(map(lambda val: val is None, values)):
            raise ValueError("provide at least one non-empty field")
        return self
