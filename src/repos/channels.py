from sqlalchemy import select

from src.repos.base import BaseRepository
from src.schemas.channels import UserChannelDTO
from src.models.users import UserContactChannel


class ChannelRepository(BaseRepository):
    model = UserContactChannel
    schema = UserChannelDTO

    async def get_all_filtered_by_ids(self, ids_list: list, **filter_by):
        query = (
            select(self.model)
            .select_from(self.model)
            .filter(
                self.model.id.in_(ids_list),
            )
            .filter_by(**filter_by)
        )
        result = await self.session.execute(query)
        return result.scalars().all()
