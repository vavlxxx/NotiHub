from typing import Dict
from fastapi.openapi.models import Example


EXAMPLE_CATEGORIES: Dict[str, Example] = {
    "ECOMMERCE": {
        "summary": "Электронная коммерция",
        "value": {
            "title": "Электронная коммерция",
            "description": "Шаблоны для интернет-магазинов: заказы, оплата, доставка",
            "parent_id": None,
        },
    },
    "USER_MANAGEMENT": {
        "summary": "Управление пользователями",
        "value": {
            "title": "Управление пользователями",
            "description": "Регистрация, авторизация, восстановление паролей",
            "parent_id": None,
        },
    },
    "HEALTHCARE": {
        "summary": "Медицинские услуги",
        "value": {
            "title": "Медицинские услуги",
            "description": "Записи к врачам, результаты анализов, напоминания",
            "parent_id": None,
        },
    },
    "FINANCE": {
        "summary": "Финансовые операции",
        "value": {
            "title": "Финансовые операции",
            "description": "Платежи, переводы, уведомления о транзакциях",
            "parent_id": None,
        },
    },
    "MARKETING": {
        "summary": "Маркетинг и промо",
        "value": {
            "title": "Маркетинг и промо",
            "description": "Рекламные рассылки, акции, персональные предложения",
            "parent_id": None,
        },
    },
    "SYSTEM": {
        "summary": "Системные уведомления",
        "value": {
            "title": "Системные уведомления",
            "description": "Техническая информация, обновления, регламентные работы",
            "parent_id": None,
        },
    },
}
