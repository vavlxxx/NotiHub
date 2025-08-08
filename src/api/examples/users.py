from typing import Dict
from fastapi.openapi.models import Example


EXAMPLE_USER_UPDATE: Dict[str, Example] = {
    "FULL_PROFILE_UPDATE": {
        "summary": "Полное обновление профиля",
        "value": {
            "first_name": "Анна",
            "last_name": "Петрова",
            "notification_enabled": True
        }
    },
    
    "PARTIAL_NAME_UPDATE": {
        "summary": "Обновление только имени",
        "value": {
            "first_name": "Иван",
            "notification_enabled": None
        }
    },
    
    "DISABLE_NOTIFICATIONS": {
        "summary": "Отключение уведомлений",
        "value": {
            "notification_enabled": False
        }
    },
    
    "ENABLE_NOTIFICATIONS": {
        "summary": "Включение уведомлений",
        "value": {
            "notification_enabled": True
        }
    },
    
    "LASTNAME_ONLY_UPDATE": {
        "summary": "Изменение только фамилии",
        "value": {
            "last_name": "Сидоров"
        }
    },
    
    "MANAGER_PROFILE": {
        "summary": "Профиль менеджера",
        "value": {
            "first_name": "Елена",
            "last_name": "Менеджерова",
            "notification_enabled": True
        }
    },
    
    "DOCTOR_PROFILE": {
        "summary": "Профиль врача",
        "value": {
            "first_name": "Александр",
            "last_name": "Докторов",
            "notification_enabled": True
        }
    },
}

EXAMPLE_USER_LOGIN: Dict[str, Example] = {
    "STANDARD_LOGIN": {
        "summary": "Стандартная авторизация",
        "value": {
            "username": "ivan_petrov",
            "password": "SecurePass123!"
        }
    },
    
    "ADMIN_LOGIN": {
        "summary": "Авторизация администратора",
        "value": {
            "username": "admin_user",
            "password": "AdminPassword2024"
        }
    },
    
    "MANAGER_LOGIN": {
        "summary": "Авторизация менеджера",
        "value": {
            "username": "manager_anna",
            "password": "ManagerPass456"
        }
    },
    
    "CLINIC_STAFF_LOGIN": {
        "summary": "Сотрудник клиники",
        "value": {
            "username": "doctor_smith",
            "password": "MedicalPass789"
        }
    },
    
    "ECOMMERCE_LOGIN": {
        "summary": "Сотрудник интернет-магазина",
        "value": {
            "username": "shop_operator",
            "password": "ShopSecure2024"
        }
    }
}
