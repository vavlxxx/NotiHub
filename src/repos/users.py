from sqlalchemy import select
from sqlalchemy.exc import NoResultFound

from src.repos.base import BaseRepository
from src.models.users import User
from src.schemas.users import UserDTO, UserPasswdDTO
from src.utils.exceptions import ObjectNotFoundError


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
    