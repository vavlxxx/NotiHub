import pytest
from httpx import AsyncClient


async def test_categories_crud(admin: AsyncClient, ac: AsyncClient):
    result = await ac.get("/categories")
    assert result and result.status_code == 200
    data = result.json()
    assert isinstance(data["data"], list)

    data_to_create = {"title": "Категория 1", "description": "Описание категории 1"}
    result = await ac.post("/categories", json=data_to_create)
    assert result and result.status_code == 403

    result = await admin.post("/categories", json=data_to_create)
    assert result and result.status_code == 200
    data = result.json()
    category_id = data["data"]["id"]
    assert category_id is not None

    result = await ac.get(f"/categories/{category_id}")
    assert result and result.status_code == 200
    data = result.json()
    new_category = data["data"]
    assert new_category["title"] == data_to_create["title"]
    assert new_category["description"] == data_to_create["description"]

    data_to_patch = {"title": "Категория 2", "description": "Описание категории 2"}
    result = await admin.patch(f"/categories/{category_id}", json=data_to_patch)
    assert result and result.status_code == 200

    result = await ac.get(f"/categories/{category_id}")
    assert result and result.status_code == 200
    data = result.json()
    assert data and data["data"]["title"] == data_to_patch["title"]
    assert data and data["data"]["description"] == data_to_patch["description"]

    result = await admin.delete(f"/categories/{category_id}")
    assert result and result.status_code == 200

    result = await ac.get(f"/categories/{category_id}")
    assert result and result.status_code == 404


@pytest.fixture(scope="module")
async def prepare_categories(db_module):
    await db_module.templates.delete(ensure_existence=False)
    await db_module.categories.delete(ensure_existence=False)
    await db_module.commit()


@pytest.mark.parametrize(
    "title, description, client_type, expected_sc, expected_count",
    [
        ("", "", "admin", 422, 0),
        ("", "Описание категории 1", "admin", 422, 0),
        ("Категория 1", "", "admin", 422, 0),
        ("Категория 1", "Описание категории 1", "ac", 403, 0),
        ("Категория 1", "Описание категории 1", "admin", 200, 1),
        ("Категория 1", "Описание категории 1", "admin", 409, 1),
    ],
)
async def test_create_categories(
    title: str,
    description: str,
    client_type: str,
    expected_sc: int,
    expected_count: int,
    request,
    prepare_categories,
):
    client = request.getfixturevalue(client_type)
    result = await client.post(
        "/categories", json={"title": title, "description": description}
    )
    assert result and result.status_code == expected_sc

    result = await client.get("/categories")
    data = result.json()
    assert isinstance(data["data"], list) and len(data["data"]) == expected_count


async def test_int32_out_of_range(admin: AsyncClient):
    result = await admin.get("/categories/2147483443344334364821474834433443343648")
    assert result.status_code == 422

    data_to_update = {"title": "Категория 1", "description": "Описание категории 1"}
    result = await admin.patch(
        "/categories/2147483443344334364821474834433443343648", json=data_to_update
    )
    assert result.status_code == 422

    await admin.delete("/categories/2147483443344334364821474834433443343648")
    assert result.status_code == 422
