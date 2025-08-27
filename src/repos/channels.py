from sqlalchemy import select
from sqlalchemy.exc import DBAPIError
from asyncpg import DataError

from src.repos.base import BaseRepository
from src.schemas.channels import ChannelDTO
from src.models.users import UserContactChannel
from src.utils.exceptions import ValueOutOfRangeError


class ChannelRepository(BaseRepository):
    model = UserContactChannel
    schema = ChannelDTO

    async def get_all_filtered_by_ids(self, ids_list: list, **filter_by):
        query = (
            select(self.model)
            .select_from(self.model)
            .filter(
                self.model.id.in_(ids_list),
            )
            .filter_by(**filter_by)
        )
        try:
            result = await self.session.execute(query)
        except DBAPIError as exc:
            if isinstance(exc.orig.__cause__, DataError):  # type: ignore
                raise ValueOutOfRangeError(detail=exc.orig.__cause__.args[0]) from exc  # type: ignore
            raise exc
        return result.scalars().all()
