from sqlalchemy import select
from sqlalchemy.exc import DBAPIError, NoResultFound
from sqlalchemy.orm import joinedload

from src.repos.base import BaseRepository
from src.models.users import User
from src.schemas.users import UserDTO, UserPasswdDTO, UserWithChannelsDTO
from src.utils.exceptions import InvalidDBDataError, ObjectNotFoundError


class UserRepository(BaseRepository):
    model = User
    schema = UserDTO

    async def get_user_with_passwd(self, **filter_by) -> UserPasswdDTO:
        query = select(self.model).filter_by(**filter_by)
        result = await self.session.execute(query)
        try:
            obj = result.scalar_one()
        except NoResultFound:
            raise ObjectNotFoundError
        return UserPasswdDTO.model_validate(obj)
    
    
    async def get_one_with_channels(self, *filter, **filter_by) -> UserDTO:
        query = (
            select(self.model)
            .filter(*filter)
            .filter_by(**filter_by)
            .options(joinedload(User.contact_channels))
        )
        try:
            result = await self.session.execute(query)
            obj = result.unique().scalar_one()
        except NoResultFound:
            raise ObjectNotFoundError
        except DBAPIError as exc:
            if isinstance(exc.orig.__cause__, DataError):  # type: ignore
                raise InvalidDBDataError from exc
            raise exc

        return UserWithChannelsDTO.model_validate(obj)
    