from datetime import datetime, timedelta, timezone

import jwt
from fastapi import Request, Response
from passlib.context import CryptContext

from schemas.channels import ChannelDTO
from src.services.base import BaseService
from src.settings import settings
from src.schemas.users import (
    UserDTO,
    UserWithPasswordDTO,
    RequestLoginUserDTO,
    RegisterUserDTO,
    RequestRegisterUserDTO,
    UserUpdateDTO,
    UserWithChannelsDTO,
)
from src.utils.enums import UserRole
from src.utils.exceptions import (
    ExpiredTokenHTTPError,
    InvalidTokenHTTPError,
    LoginDataError,
    ObjectExistsError,
    ObjectNotFoundError,
    UserExistsError,
    UserNotFoundError,
)


class UserService(BaseService):
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


    def _hash_password(self, password) -> str:
        return self.pwd_context.hash(password)


    def _verify_password(self, plain_password, password_hash):
        return self.pwd_context.verify(plain_password, password_hash)


    async def add_user(self, user_data: RequestRegisterUserDTO, user_meta: dict | None = None):
        password_hash = self._hash_password(user_data.password)
        fields_to_eclude = {"password"}
        if user_meta and not user_meta.get("is_admin"):
            fields_to_eclude.add("role")

        data = user_data.model_dump(exclude=fields_to_eclude)
        new_user_data = RegisterUserDTO(**data, password_hash=password_hash)

        try:
            await self.db.users.add(new_user_data)
        except ObjectExistsError as exc:
            raise UserExistsError from exc
        await self.db.commit()


    async def edit_user(self, user_data: UserUpdateDTO, user_meta: dict):
        try:
            await self.db.users.get_one(id=user_meta.get("user_id", 0))
        except ObjectNotFoundError as exc:
            raise UserNotFoundError from exc
        
        if not user_meta.get("is_admin"):
            user_data = UserUpdateDTO(**user_data.model_dump(exclude={"role"}))

        await self.db.users.edit(user_data, id=user_meta.get("user_id", 0))
        await self.db.commit()


    async def login_user(self, user_data: RequestLoginUserDTO, response: Response, request: Request):
        try:
            user: UserWithPasswordDTO = await self.db.users.get_user_with_passwd(username=user_data.username)
        except ObjectNotFoundError as exc:
            raise LoginDataError from exc

        if not self._verify_password(user_data.password, user.password_hash):
            raise LoginDataError

        token_data = {"user_id": user.id, "is_admin": False}
        if user.role == UserRole.ADMIN:
            token_data["is_admin"] = True

        access_token, expire = self.create_access_token(token_data)
        response.set_cookie(key="access_token", value=access_token)
        return access_token, expire


    async def get_user(self, *filter, include_channels: bool = True, **filter_by) -> UserDTO | UserWithChannelsDTO:
        try:
            user: UserDTO = await self.db.users.get_one(*filter, **filter_by)
        except ObjectNotFoundError as exc:
            raise UserNotFoundError from exc

        if include_channels:
            channels: list[ChannelDTO] = await self.db.channels.get_all_filtered(user_id=user.id) 
            user_: UserWithChannelsDTO = UserWithChannelsDTO(**user.model_dump(), channels=channels)
            return user_
        return user


    @staticmethod
    def create_access_token(data: dict):
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
        )
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(
            to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
        )
        return encoded_jwt, expire


    @staticmethod
    def decode_access_token(access_token) -> dict[str, str]:
        try:
            return jwt.decode(
                access_token,
                settings.JWT_SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM],
            )
        except jwt.exceptions.DecodeError:
            raise InvalidTokenHTTPError
        except jwt.exceptions.ExpiredSignatureError:
            raise ExpiredTokenHTTPError
