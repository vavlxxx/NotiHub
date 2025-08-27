from httpx import AsyncClient


async def test_channels_int32_out_of_range(admin: AsyncClient):
    data_to_update = {
        "contact_value": "1324567",
        "channel_type": "TELEGRAM",
    }
    result = await admin.patch("/channels/21474834433443343648", json=data_to_update)
    assert result.status_code == 422

    await admin.delete("/channels/99999999999999999999")
    assert result.status_code == 422
