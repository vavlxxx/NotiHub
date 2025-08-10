from src.schemas.base import BaseDTO
from src.utils.enums import ContactChannelType


class UserChannelAddRequestDTO(BaseDTO):
    contact_value: str
    channel_type: ContactChannelType
    
class UserChannelAddDTO(UserChannelAddRequestDTO):
    user_id: int
    contact_value: str
    channel_type: ContactChannelType

class UserChannelDTO(BaseDTO):
    id: int
    contact_value: str
    channel_type: ContactChannelType
    is_active: bool

class UserChannelUpdateDTO(BaseDTO):
    contact_value: str | None = None
    channel_type: ContactChannelType | None = None
    is_active: bool | None = None
