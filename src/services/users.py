from datetime import datetime, timedelta, timezone

import jwt
from fastapi import HTTPException
from passlib.context import CryptContext

from src.services.base import BaseService
from src.settings import settings
from src.schemas.users import (
    UserPasswdDTO,
    UserLoginRequestDTO,
    UserRegisterDTO,
    UserRegisterRequestDTO,
    UserUpdateDTO,
)
from src.utils.exceptions import (
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

    async def add_user(self, user_data: UserRegisterRequestDTO):
        password_hash = self._hash_password(user_data.password)
        data = user_data.model_dump(exclude={"password"})
        new_user_data = UserRegisterDTO(**data, password_hash=password_hash)

        try:
            await self.db.users.add(new_user_data)
        except ObjectExistsError as exc:
            raise UserExistsError from exc
        await self.db.commit()

    async def edit_user(self, user_data: UserUpdateDTO, user_id: int):
        try:
            await self.db.users.get_one(id=user_id)
        except ObjectNotFoundError as exc:
            raise UserNotFoundError from exc
        await self.db.users.edit(user_data, id=user_id)
        await self.db.commit()

    async def login_user(self, user_data: UserLoginRequestDTO, response):
        try:
            user: UserPasswdDTO = await self.db.users.get_user_with_passwd(username=user_data.username)
        except ObjectNotFoundError as exc:
            raise LoginDataError from exc

        if not self._verify_password(user_data.password, user.password_hash):
            raise LoginDataError

        token_data = {"user_id": user.id}
        if user_data.username == settings.DB_ADMIN_LOGIN:
            token_data["is_admin"] = True

        access_token = self.create_access_token(token_data)
        response.set_cookie(key="access_token", value=access_token)
        return access_token

    async def get_user(self, *filter, exclude_channels: bool = False, **filter_by):
        try:
            if exclude_channels:
                user = await self.db.users.get_one(*filter, **filter_by)
                return user
            
            user = await self.db.users.get_one_with_channels(*filter, **filter_by)
        except ObjectNotFoundError as exc:
            raise UserNotFoundError from exc
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
        return encoded_jwt

    @staticmethod
    def decode_access_token(access_token) -> dict[str, str]:
        try:
            return jwt.decode(
                access_token,
                settings.JWT_SECRET_KEY,
                algorithms=[settings.JWT_ALGORITHM],
            )
        except jwt.exceptions.DecodeError:
            raise HTTPException(status_code=401, detail="Неверный токен")
        except jwt.exceptions.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Срок действия токена истёк. Пожалуйста пройдите аутентификацию заново")
    