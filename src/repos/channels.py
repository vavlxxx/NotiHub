from src.repos.base import BaseRepository
from src.schemas.channels import UserChannelDTO
from src.models.users import UserContactChannel


class ChannelRepository(BaseRepository):
    model = UserContactChannel
    schema = UserChannelDTO
