from typing import Any
from httpx import AsyncClient
import pytest


async def test_templates_crud(admin: AsyncClient):
    data_to_create = {
        "title": "Подтверждение заказа",
        "content": "Здравствуйте, {{ username }}! Ваш заказ № {{ order_id }} успешно оформлен!",
        "description": "Текстовый шаблон для подтверждения заказа в интернет-магазине",
    }
    result = await admin.post("/templates", json=data_to_create)

    assert result.status_code == 200
    data = result.json()
    assert data is not None
    assert isinstance(data, dict)
    assert data.get("data") is not None
    template_id = data["data"]["id"]

    result = await admin.get(f"/templates/{template_id}")
    assert result.status_code == 200
    data = result.json()
    assert data is not None
    assert isinstance(data, dict)
    assert data.get("data") is not None
    template = data["data"]

    assert data_to_create["content"] == template["content"]
    assert data_to_create["description"] == template["description"]
    assert data_to_create["title"] == template["title"]

    result = await admin.patch(f"/templates/{template_id}", json={"content": "123"})
    assert result.status_code == 200

    result = await admin.get(f"/templates/{template_id}")
    data = result.json()
    template = data["data"]
    assert template["content"] == "123"

    result = await admin.delete(f"/templates/{template_id}")
    assert result.status_code == 200

    result = await admin.get(f"/templates/{template_id}")
    assert result.status_code == 404


@pytest.fixture(scope="module")
async def prepare_templates(db_module):
    await db_module.templates.delete(ensure_existence=False)
    await db_module.commit()


@pytest.mark.parametrize(
    "title, content, category_id, expected_sc, expected_count",
    [
        ("", "", None, 422, 0),
        ("Шаблон", "", None, 422, 0),
        ("", "Шаблон", None, 422, 0),
        (
            "Шаблон оформления заказа",
            "Здравствуйте, {{ username }}! Ваш заказ № {{ order_id }} успешно оформлен!",
            None,
            200,
            1,
        ),
        (
            "Шаблон с несуществующей категорией",
            "Здравствуйте, {{ username }}! Ваш заказ № {{ order_id }} успешно оформлен!",
            168769,
            404,
            1,
        ),
        (
            "Шаблон с ошибкой синтаксиса",
            "Здравствуйте, {{ username ! Ваш заказ № {{ order_id }} успешно оформлен!",
            None,
            422,
            1,
        ),
        ("Шаблон приветствия", "Здравствуйте, {{ username }}!", None, 200, 2),
    ],
)
async def test_create_templates(
    title: str,
    content: str,
    category_id: int | None,
    expected_sc: int,
    expected_count: int,
    admin: AsyncClient,
    prepare_templates,
):
    data_to_post: dict[str, Any] = {
        "title": title,
        "content": content,
    }
    if category_id:
        data_to_post["category_id"] = category_id

    result = await admin.post(
        "/templates",
        json={"title": title, "content": content, "category_id": category_id},
    )
    assert result.status_code == expected_sc

    result = await admin.get("/templates")
    data = result.json()
    templates = data["data"]
    assert len(templates) == expected_count


async def test_int32_out_of_range(admin: AsyncClient):
    goofy_params = {
        "category_id": 34343343443343434433434334344334343443,
        "limit": 15,
        "offset": 34343343443343434433434334344334343443,
    }
    result = await admin.get("/templates", params=goofy_params)
    assert result.status_code == 422

    result = await admin.get("/templates/21474834433443343648")
    assert result.status_code == 422

    data_to_update = {"title": "Шаблончик 1"}
    result = await admin.patch("/templates/99999999999999999999", json=data_to_update)
    assert result.status_code == 422

    await admin.delete("/templates/99999999999999999999")
    assert result.status_code == 422
