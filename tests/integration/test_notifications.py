from unittest import mock

import pytest
from httpx import AsyncClient

from src.schemas.channels import AddChannelDTO
from src.schemas.templates import AddTemplateDTO
from src.services.users import UserService
from src.schemas.categories import AddCategoryDTO
from src.utils.enums import ContactChannelType, ScheduleType
from src.settings import settings


class MockedTask:
    def delay(self, *args, **kwargs):
        pass


mock.patch(
    "src.services.notifications.CELERY_TASKS",
    {
        ContactChannelType.EMAIL: MockedTask(),
        ContactChannelType.TELEGRAM: MockedTask(),
        ContactChannelType.PUSH: MockedTask(),
    },
).start()


@pytest.fixture(scope="module")
async def prepare_db(db_module, admin: AsyncClient):
    await db_module.templates.delete(ensure_existence=False)
    await db_module.categories.delete(ensure_existence=False)

    result = await db_module.categories.add(AddCategoryDTO(title="Категория Тест"))
    assert result and result.id is not None
    category_id = result.id

    token = admin.cookies.get("access_token")
    assert token
    user_id = int(UserService.decode_access_token(token)["user_id"])
    assert user_id

    result = await db_module.templates.add(
        AddTemplateDTO(
            title="Шаблон из теста",
            content="Шаблон {{ var2 }} Тест {{ var1 }}",
            category_id=category_id,
            user_id=user_id,
        )
    )
    assert result and result.id is not None
    template_id = result.id

    result = await db_module.channels.add(
        AddChannelDTO(
            channel_type=ContactChannelType.TELEGRAM,
            contact_value=settings.TELEGRAM_ADMIN_CONTACT,
            user_id=user_id,
        )
    )
    assert result and result.id is not None
    channel_id = result.id

    await db_module.commit()
    return {"user_id": user_id, "template_id": template_id, "channel_id": channel_id}


@pytest.mark.parametrize(
    "schedule_type, template_id, channels_ids, variables, expected_sc",
    [
        (
            "ONCE",
            454665566554545454,
            [],
            {"var1": "123", "var2": "456"},
            422,
        ),
        ("ONCE", 0, [4546655665545454544], {"var1": "123", "var2": "456"}, 422),
        ("", 0, [], {"var1": "123", "var2": "456"}, 422),
        ("ONCE", 0, [], {}, 422),
        ("ONCE", 0, [], {"var2": "456"}, 422),
        ("ONCE", 0, [], {"var1": "123", "var2": "456"}, 200),
        ("ONCE", 0, [], {}, 422),
    ],
)
async def test_notifications(
    schedule_type: ScheduleType,
    template_id: int,
    channels_ids: list[int],
    variables: dict[str, str],
    expected_sc: int,
    admin: AsyncClient,
    prepare_db,
):
    noti_data = {
        "schedule_type": schedule_type,
        "template_id": template_id,
        "channels_ids": channels_ids,
        "variables": variables,
    }

    if not channels_ids:
        noti_data["channels_ids"] = [prepare_db["channel_id"]]
    if template_id == 0:
        noti_data["template_id"] = prepare_db["template_id"]

    # print(noti_data)
    result = await admin.post("/notifications/sendOne", json=noti_data)
    # print(result.json())
    assert result.status_code == expected_sc
