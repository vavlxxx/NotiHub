from fastapi import APIRouter, Body, Response

from src.api.examples.users import EXAMPLE_USER_LOGIN, EXAMPLE_USER_UPDATE
from src.services.users import UserService

from src.dependencies.db import DBDep
from src.dependencies.users import UID_Dep
from src.utils.exceptions import (
    LoginDataError,
    LoginDataHTTPError,
    UserNotFoundError,
    UserNotFoundHTTPError,
    UserExistsError,
    UserExistsHTTPError,
)

from src.schemas.users import UserRegisterRequestDTO, UserLoginRequestDTO, UserUpdateDTO


router = APIRouter(prefix="/auth", tags=["Авторизация и Аутентификация"])


@router.post("/register", summary="Зарегистрироваться")
async def register_user(
    db: DBDep,
    user_data: UserRegisterRequestDTO = Body(description="Логин и пароль", openapi_examples=EXAMPLE_USER_LOGIN)
):
    try:
        await UserService(db).add_user(user_data)
    except UserExistsError as exc:
        raise UserExistsHTTPError from exc

    return {"status": "OK"}


@router.post("/login", summary="Пройти аутентификацию")
async def login_user(
    db: DBDep,
    response: Response = Response(status_code=200),
    user_data: UserLoginRequestDTO = Body(description="Логин и пароль", openapi_examples=EXAMPLE_USER_LOGIN)
):
    try:
        access_token = await UserService(db).login_user(response=response, user_data=user_data)
    except LoginDataError as exc:
        raise LoginDataHTTPError from exc

    return {"status": "OK", "access_token": access_token}


@router.patch("/edit", summary="Обновить профиль пользователя")
async def edit_user(
    user_id: UID_Dep,
    db: DBDep,
    user_data: UserUpdateDTO = Body(description="Данные о пользователе", openapi_examples=EXAMPLE_USER_UPDATE)
):
    try:
        await UserService(db).edit_user(user_data, user_id=user_id)
    except UserNotFoundError as exc:
        raise UserNotFoundHTTPError from exc
    return {"status": "OK"}


@router.get("/me", summary="Получить профиль аутентифицированного пользователя")
async def only_auth(user_id: UID_Dep, db: DBDep):
    try:
        user = await UserService(db).get_user(user_id=user_id)
    except UserNotFoundError as exc:
        raise UserNotFoundHTTPError from exc
    return user


@router.post("/logout", summary="Выйти из аккаунта")
async def logout_user(_: UID_Dep, response: Response = Response(status_code=200)):
    response.delete_cookie(key="access_token")
    return {"status": "OK"}
