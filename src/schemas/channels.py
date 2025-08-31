from typing import Annotated, Union
from pydantic import EmailStr, model_validator
from pydantic import validate_email
from pydantic_extra_types.phone_numbers import PhoneNumber, PhoneNumberValidator
from src.schemas.base import BaseDTO
from src.utils.enums import ContactChannelType

E164Number = Annotated[
    Union[str, PhoneNumber],
    PhoneNumberValidator(
        default_region="RU",
        number_format="E164",
        supported_regions=["RU", "KZ", "UA", "US"],
    ),
]


class RequestAddChannelDTO(BaseDTO):
    contact_value: str | EmailStr | PhoneNumber
    channel_type: ContactChannelType

    @model_validator(mode="after")
    def validate_channel_type(self):
        cv = self.contact_value
        match self.channel_type:
            case ContactChannelType.TELEGRAM:
                if not cv.isdigit():
                    raise ValueError("telegram may be only as numeric telegram_id")
            case ContactChannelType.EMAIL:
                if not validate_email(cv):
                    raise ValueError("email must be valid string with @ and domain")
            # case ContactChannelType.SMS:
            #     try:
            #         from phonenumbers import (
            #             parse,
            #             is_valid_number,
            #             format_number,
            #             PhoneNumberFormat,
            #         )

            #         parsed = parse(self.contact_value, "RU")
            #         if not is_valid_number(parsed):
            #             raise ValueError("Неверный номер телефона")
            #         formatted = format_number(parsed, PhoneNumberFormat.E164)
            #         self.contact_value = formatted.lstrip("+")

            #     except Exception as exc:
            #         raise ValueError(
            #             f"phone number must be valid (E.164 or local with default_region): {exc}"
            #         )

            case ContactChannelType.PUSH:
                pass
        return self


class AddChannelDTO(RequestAddChannelDTO):
    user_id: int


class ChannelDTO(BaseDTO):
    id: int
    contact_value: EmailStr | str
    channel_type: ContactChannelType


class ChannelWithUserDTO(ChannelDTO):
    user_id: int


class UpdateChannelDTO(BaseDTO):
    contact_value: EmailStr | str | None = None
    channel_type: ContactChannelType | None = None

    @model_validator(mode="after")
    def validate_all_fields_are_providen(self):
        values = tuple(self.model_dump().values())
        if all(map(lambda val: val is None, values)):
            raise ValueError("provide at least one non-empty field")
        return self
