from typing import Dict
from fastapi.openapi.models import Example

EXAMPLE_USER_UPDATE: Dict[str, Example] = {
    "FULL_PROFILE_UPDATE": {
        "summary": "Полное обновление профиля",
        "value": {
            "first_name": "Анна",
            "last_name": "Петрова"
        }
    },
    
    "PARTIAL_NAME_UPDATE": {
        "summary": "Обновление только имени",
        "value": {
            "first_name": "Дмитрий"
        }
    },
    
    "LASTNAME_ONLY_UPDATE": {
        "summary": "Изменение только фамилии",
        "value": {
            "last_name": "Козлов"
        }
    },
    
    "MANAGER_PROFILE": {
        "summary": "Профиль менеджера",
        "value": {
            "first_name": "Елена",
            "last_name": "Волкова"
        }
    },
    
    "DOCTOR_PROFILE": {
        "summary": "Профиль врача",
        "value": {
            "first_name": "Александр",
            "last_name": "Медведев"
        }
    },
    
    "TEACHER_PROFILE": {
        "summary": "Профиль преподавателя",
        "value": {
            "first_name": "Мария",
            "last_name": "Кузнецова"
        }
    },
    
    "DEVELOPER_PROFILE": {
        "summary": "Профиль разработчика",
        "value": {
            "first_name": "Сергей",
            "last_name": "Попов"
        }
    },
    
    "ACCOUNTANT_PROFILE": {
        "summary": "Профиль бухгалтера",
        "value": {
            "first_name": "Ольга",
            "last_name": "Морозова"
        }
    }
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
            "username": "elena_volkova",
            "password": "ManagerPass456"
        }
    },
    
    "DOCTOR_LOGIN": {
        "summary": "Авторизация врача",
        "value": {
            "username": "doctor_medvedev",
            "password": "MedicalPass789"
        }
    },
    
    "SHOP_OPERATOR": {
        "summary": "Оператор интернет-магазина",
        "value": {
            "username": "shop_operator",
            "password": "ShopSecure2024"
        }
    },
    
    "TEACHER_LOGIN": {
        "summary": "Авторизация преподавателя",
        "value": {
            "username": "maria_teacher",
            "password": "TeachPass2024"
        }
    },
    
    "DEVELOPER_LOGIN": {
        "summary": "Авторизация разработчика",
        "value": {
            "username": "dev_sergey",
            "password": "DevSecure789"
        }
    },
    
    "FINANCE_LOGIN": {
        "summary": "Авторизация финансиста",
        "value": {
            "username": "finance_olga",
            "password": "FinancePass456"
        }
    }
}