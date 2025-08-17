import pytest
from httpx import AsyncClient


@pytest.mark.parametrize("username, password, expected_sc", [
    ("", "SecurePass123!", 422),
    ("ivan_petrov", "", 422),
    ("ivan_petrov", "SecurePass123!", 409),
    ("ivan", "qwerty12345", 200),
])
async def test_user_register(
    username: str,
    password: str,
    expected_sc: int,
    ac: AsyncClient
):
    resp = await ac.post("/auth/register", json={"username": username, "password": password})
    assert resp and resp.status_code == expected_sc


async def test_register_new_admin(
    admin: AsyncClient
):
    resp = await admin.post("/auth/register", json={"username": "admin2", "password": "admin123456789", "role": "ADMIN"})
    assert resp and resp.status_code == 200

    resp = await admin.post("/auth/logout")
    assert resp and resp.status_code == 200

    resp = await admin.post("/auth/login", json={"username": "admin2", "password": "admin123456789"})
    assert resp and resp.status_code == 200

    resp = await admin.get("/auth/me")
    assert resp and resp.status_code == 200
    data = resp.json()
    assert data["data"]["username"] == "admin2"
    assert data["data"]["role"] == "ADMIN"
    


@pytest.mark.parametrize("username, password, expected_sc", [
    ("", "qwerty12345", 422), 
    ("ivan_petrov", "", 422),
    ("gfunnnnfhpih", "34344334t643fg", 401),
    ("ivan", "qwerty12345", 200),
])
async def test_user_login(
    username: str,
    password: str,
    expected_sc: int,
    ac: AsyncClient
):
    resp = await ac.post("/auth/login", json={"username": username, "password": password})
    assert resp and resp.status_code == expected_sc
    