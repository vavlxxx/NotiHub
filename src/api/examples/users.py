from typing import Dict
from fastapi.openapi.models import Example

EXAMPLE_USER_UPDATE: Dict[str, Example] = {
    "FULL_PROFILE_UPDATE": {
        "summary": "Полное обновление профиля",
        "value": {"first_name": "Анна", "last_name": "Петрова"},
    },
    "PARTIAL_NAME_UPDATE": {
        "summary": "Обновление только имени",
        "value": {"first_name": "Дмитрий"},
    },
    "LASTNAME_ONLY_UPDATE": {
        "summary": "Изменение только фамилии",
        "value": {"last_name": "Козлов"},
    },
    "MANAGER_PROFILE": {
        "summary": "Пример 1",
        "value": {"first_name": "Елена", "last_name": "Волкова"},
    },
    "DOCTOR_PROFILE": {
        "summary": "Пример 2",
        "value": {"first_name": "Александр", "last_name": "Медведев"},
    },
    "TEACHER_PROFILE": {
        "summary": "Пример 3",
        "value": {"first_name": "Мария", "last_name": "Кузнецова"},
    },
    "DEVELOPER_PROFILE": {
        "summary": "Пример 4",
        "value": {"first_name": "Сергей", "last_name": "Попов"},
    },
    "ACCOUNTANT_PROFILE": {
        "summary": "Пример 5",
        "value": {"first_name": "Ольга", "last_name": "Морозова"},
    },
}

EXAMPLE_USER_LOGIN: Dict[str, Example] = {
    "STANDARD_LOGIN": {
        "summary": "Пользователь 1",
        "value": {"username": "ivan_petrov", "password": "SecurePass123!"},
    },
    "MANAGER_LOGIN": {
        "summary": "Пользователь 2",
        "value": {"username": "elena_volkova", "password": "ManagerPass456"},
    },
    "DOCTOR_LOGIN": {
        "summary": "Пользователь 3",
        "value": {"username": "doctor_medvedev", "password": "MedicalPass789"},
    },
    "SHOP_OPERATOR": {
        "summary": "Пользователь 4",
        "value": {"username": "shop_operator", "password": "ShopSecure2024"},
    },
    "TEACHER_LOGIN": {
        "summary": "Пользователь 5",
        "value": {"username": "maria_teacher", "password": "TeachPass2024"},
    },
    "DEVELOPER_LOGIN": {
        "summary": "Пользователь 6",
        "value": {"username": "dev_sergey", "password": "DevSecure789"},
    },
    "FINANCE_LOGIN": {
        "summary": "Пользователь 7",
        "value": {"username": "finance_olga", "password": "FinancePass456"},
    },
}
