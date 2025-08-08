from typing import Annotated

from fastapi import Depends, Request

from src.services.users import UserService
from src.utils.exceptions import NotAuthenticatedError


def get_access_token(request: Request):
    access_token = request.cookies.get("access_token", None)
    if access_token is None:
        raise NotAuthenticatedError
    return access_token


def get_user_id_from_request(access_token: str = Depends(get_access_token)):
    data = UserService.decode_access_token(access_token=access_token)
    return data.get("user_id", 0)
    

UID_Dep = Annotated[int, Depends(get_user_id_from_request)]
