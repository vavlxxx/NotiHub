from typing import AsyncGenerator

from unittest import mock

mock.patch("fastapi_cache.decorator.cache", lambda *args, **kwargs: lambda x: x).start()

import pytest
from httpx import ASGITransport, AsyncClient

from src.main import app
from src.utils.enums import UserRole
from src.dependencies.db import get_db
from src.schemas.users import RequestRegisterUserDTO
from src.db import sessionmaker_null_pool, engine_null_pool
from src.settings import settings
from src.utils.db_manager import DB_Manager
from src.services.users import UserService
from src.models import *


###
async def get_db_with_null_pool() -> AsyncGenerator[DB_Manager, None]:
    async with DB_Manager(session_factory=sessionmaker_null_pool) as db:
        yield db
app.dependency_overrides[get_db] = get_db_with_null_pool

@pytest.fixture()
async def db():
    async for db in get_db_with_null_pool():
        yield db
###


@pytest.fixture(scope="session", autouse=True)
async def check_test_mode():
    assert settings.MODE == "TEST"
    assert settings.DB_NAME == "test_notihub_db"

@pytest.fixture(scope="session", autouse=True)
async def main(check_test_mode):
    async with engine_null_pool.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    async with DB_Manager(session_factory=sessionmaker_null_pool) as db:
        await db.check_connection()

        await UserService(db).add_user(
            RequestRegisterUserDTO(
                username=settings.DB_ADMIN_LOGIN, 
                password=settings.DB_ADMIN_PASSWORD,
                role=UserRole.ADMIN
            )
        )


@pytest.fixture(scope="session")
async def client() -> AsyncGenerator[AsyncClient, None]:
    app_ = ASGITransport(app=app)
    async with AsyncClient(transport=app_, base_url="http://test") as client:
        yield client


@pytest.fixture(scope="session", autouse=True)
async def ac(main, client):
    resp = await client.post(
        "/auth/register",
        json={
            "username": "ivan_petrov",
            "password": "SecurePass123!"
        }
    )
    assert resp
    assert resp.status_code == 200

    resp = await client.post(
        "/auth/login",
        json={
            "username": "ivan_petrov",
            "password": "SecurePass123!"
        }
    )
    assert resp
    assert resp.status_code == 200
    data = resp.json()
    access_token = data.get("access_token")
    decoded_token = UserService.decode_access_token(access_token=access_token)
    assert decoded_token.get("is_admin", False) == False
    
    assert access_token is not None
    cookies_token = client.cookies.get("access_token")
    assert cookies_token is not None
    assert cookies_token == access_token
    yield client


@pytest.fixture(scope="session", autouse=True)
async def admin(main, client):
    resp = await client.post(
        "/auth/login",
        json={
            "username": settings.DB_ADMIN_LOGIN,
            "password": settings.DB_ADMIN_PASSWORD
        },
    )
    assert resp
    assert resp.status_code == 200
    assert isinstance(resp.json(), dict)
    
    data = resp.json()
    access_token = data.get("access_token")
    decoded_token = UserService.decode_access_token(access_token=access_token)
    assert decoded_token.get("is_admin", True)
    
    assert access_token is not None
    cookies_token = client.cookies.get("access_token")
    assert cookies_token is not None
    assert cookies_token == access_token
    yield client
