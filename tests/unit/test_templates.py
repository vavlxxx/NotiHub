from httpx import AsyncClient
import pytest


async def test_templates_crud(admin: AsyncClient):
    data_to_create = {
        "title": "Подтверждение заказа",
        "content": "Здравствуйте, {{ username }}! Ваш заказ № {{ order_id }} успешно оформлен!",
        "description": "Текстовый шаблон для подтверждения заказа в интернет-магазине"
    }
    result = await admin.post("/templates/", json=data_to_create)

    assert result.status_code == 200
    data = result.json()
    assert data is not None
    assert isinstance(data, dict)
    assert data.get("data") is not None
    template_id = data["data"]["id"]

    result = await admin.get(f"/templates/{template_id}/")
    assert result.status_code == 200
    data = result.json()
    assert data is not None
    assert isinstance(data, dict)
    assert data.get("data") is not None
    template = data["data"]

    assert data_to_create["content"] == template["content"]
    assert data_to_create["description"] == template["description"]
    assert data_to_create["title"] == template["title"]

    result = await admin.patch(f"/templates/{template_id}/", json={"content": "123"})
    assert result.status_code == 200

    result = await admin.get(f"/templates/{template_id}/")
    data = result.json()
    template = data["data"]
    assert template["content"] == "123"

    result = await admin.delete(f"/templates/{template_id}/")
    assert result.status_code == 200

    result = await admin.get(f"/templates/{template_id}/")
    assert result.status_code == 404


@pytest.mark.parametrize("title, content, category_id, expected_sc, expected_count", [
    ("Шаблон оформления заказа", "Здравствуйте, {{ username }}! Ваш заказ № {{ order_id }} успешно оформлен!", 1, 200, 1), 
    ("Шаблон с несуществующей категорией", "Здравствуйте, {{ username }}! Ваш заказ № {{ order_id }} успешно оформлен!", 19, 404, 1), 
    ("Шаблон с ошибкой синтаксиса", "Здравствуйте, {{ username ! Ваш заказ № {{ order_id }} успешно оформлен!", 1, 422, 1),
    ("Шаблон приветствия", "Здравствуйте, {{ username }}!", 1, 200, 2),
])
async def test_templates_operations(
    title: str,
    content: str,
    category_id: int,
    expected_sc: int,
    expected_count: int,
    admin: AsyncClient
):
    result = await admin.post(
        "/templates/", 
        json={
            "title": title,
            "content": content,
            "category_id": category_id
        }
    )
    assert result.status_code == expected_sc

    result = await admin.get("/templates/")
    data = result.json()
    templates = data["data"]
    assert len(templates) == expected_count
