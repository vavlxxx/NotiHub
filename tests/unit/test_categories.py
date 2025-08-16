from httpx import AsyncClient


async def test_categories_crud(admin: AsyncClient, ac: AsyncClient):
    result = await ac.get("/categories/")
    assert result and result.status_code == 200
    data = result.json()
    assert isinstance(data["data"], list)
