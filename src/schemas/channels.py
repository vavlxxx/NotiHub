from pydantic import model_validator

from src.schemas.base import BaseDTO
from src.utils.enums import ContactChannelType


class RequestAddChannelDTO(BaseDTO):
    contact_value: str
    channel_type: ContactChannelType
    
class AddChannelDTO(RequestAddChannelDTO):
    user_id: int
    contact_value: str
    channel_type: ContactChannelType

class ChannelDTO(BaseDTO):
    id: int
    contact_value: str
    channel_type: ContactChannelType

class UpdateChannelDTO(BaseDTO):
    contact_value: str | None = None
    channel_type: ContactChannelType | None = None

    @model_validator(mode="after")
    def validate_all_fields_are_providen(self):
        values = tuple(self.model_dump().values())
        if all(map(lambda val: val is None, values)):
            raise ValueError("provide at least one non-empty field")
        return self
