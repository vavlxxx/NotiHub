from typing import Annotated

from fastapi import Depends, Request

from src.services.users import UserService
from src.utils.exceptions import NotAuthenticatedError, OnlyStaffHTTPError


def get_access_token(request: Request):
    return request.cookies.get("access_token", None)


def auth_required(access_token: str = Depends(get_access_token)):
    if access_token is None:
        raise NotAuthenticatedError
    return access_token


def only_staff(access_token: str = Depends(auth_required)):
    data = UserService.decode_access_token(access_token=access_token)
    if not (is_admin := data.get("is_admin", False)):
        raise OnlyStaffHTTPError
    return is_admin


def get_user_meta_from_request(access_token: str = Depends(get_access_token)):
    data = {}
    if access_token is not None:
        data = UserService.decode_access_token(access_token=access_token)
    
    user_meta = {
        "user_id": data.get("user_id", 0),
        "is_admin": data.get("is_admin", False),
    }
    return user_meta

UserMetaDep = Annotated[dict, Depends(get_user_meta_from_request)]
