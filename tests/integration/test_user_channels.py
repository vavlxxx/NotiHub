import pytest
from httpx import AsyncClient


@pytest.mark.parametrize(
    "channel_type, contact_value, expected_sc, total_count",
    [
        ("", "", 422, 0),
        ("", "12345678", 422, 0),
        ("TELEGRAM", "", 422, 0),
        ("TELEGRAM", "12345678", 200, 1),
        ("TELEGRAM", "12d4fd6gf8", 422, 1),
        ("TELEGRAM", "@username123", 422, 1),
        ("TELEGRAM", "@", 422, 1),
        ("EMAIL", "", 422, 1),
        ("EMAIL", "12345678", 422, 1),
        ("EMAIL", "mail@gmail.com", 200, 2),
    ],
)
async def test_create_user_channels(
    channel_type: str,
    contact_value: str,
    expected_sc: int,
    total_count: int,
    ac: AsyncClient,
):
    result = await ac.post(
        "/channels", json={"channel_type": channel_type, "contact_value": contact_value}
    )
    assert result and result.status_code == expected_sc

    result = await ac.get("/auth/me")
    assert result and result.status_code == 200
    data = result.json()
    assert (
        isinstance(data["data"]["channels"], list)
        and len(data["data"]["channels"]) == total_count
    )


async def create_and_update_channel(ac: AsyncClient):
    result = await ac.post(
        "/channels", json={"channel_type": "TELEGRAM", "contact_value": "12334567890"}
    )
    assert result and result.status_code == 200
    channel_id = result.json()["data"]["id"]

    result = await ac.patch(
        f"/channels/{channel_id}",
        json={"channel_type": "TELEGRAM", "contact_value": "1@gmail.com"},
    )
    assert result and result.status_code == 422
