from typing import Dict
from fastapi.openapi.models import Example


EXAMPLE_TEMPLATES: Dict[str, Example] = {
    # ЭЛЕКТРОННАЯ КОММЕРЦИЯ (ECOMMERCE)
    "ORDER_CONFIRMATION": {
        "summary": "Подтверждение заказа",
        "value": {
            "title": "Подтверждение заказа",
            "content": "Здравствуйте, {{ username }}! Ваш заказ № {{ order_id }} на сумму {{ amount }} руб. успешно оформлен и принят в обработку. Ожидаемая дата доставки: {{ delivery_date }}.",
            "category_id": 1,  # ECOMMERCE
            "description": "Текстовый шаблон для подтверждения заказа в интернет-магазине",
        },
    },
    "ORDER_SHIPPED_HTML": {
        "summary": "Заказ отправлен (HTML)",
        "value": {
            "title": "Ваш заказ в пути!",
            "content": """<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>Заказ отправлен</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; background-color: #f8f9fa; }
        .container { background: white; padding: 30px; border-radius: 10px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); }
        .header { text-align: center; color: #28a745 !important; margin-bottom: 20px; }
        .order-info { background: #e8f5e8; padding: 15px; border-radius: 5px; margin: 15px 0; }
        .track-btn { display: inline-block; background: #007bff; color: white !important; padding: 12px 25px; text-decoration: none; border-radius: 5px; margin-top: 15px; }
        .footer { text-align: center; color: #666 !important; margin-top: 20px; font-size: 14px; }
    </style>
</head>
<body>
    <div class="container">
        <h1 class="header">📦 Заказ отправлен!</h1>
        <p>Привет, {{ username }}!</p>
        <div class="order-info">
            <strong>Заказ:</strong> {{ order_id }}<br>
            <strong>Трек-номер:</strong> {{ tracking_number }}
        </div>
        <p>Ваш заказ передан в службу доставки и скоро будет у вас!</p>
        <div style="text-align: center;">
            <a href="{{ tracking_link }}" class="track-btn">Отследить посылку</a>
        </div>
        <div class="footer">Спасибо за покупку! 💙</div>
    </div>
</body>
</html>""",
            "category_id": 1,  # ECOMMERCE
            "description": "HTML шаблон уведомления об отправке заказа с трекингом",
        },
    },
    "CART_ABANDONED": {
        "summary": "Забытая корзина",
        "value": {
            "title": "Вы забыли про корзину",
            "content": "{{ username }}, в вашей корзине ждут {{ items_count }} товаров на {{ total_amount }} руб. Завершите покупку в течение 24 часов и получите скидку {{ discount }}%!",
            "category_id": 1,  # ECOMMERCE
            "description": "Напоминание о незавершенной покупке",
        },
    },
    # УПРАВЛЕНИЕ ПОЛЬЗОВАТЕЛЯМИ (USER_MANAGEMENT)
    "WELCOME_NEW_USER_HTML": {
        "summary": "Добро пожаловать (HTML)",
        "value": {
            "title": "Добро пожаловать в {{ service_name }}!",
            "content": """<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>Добро пожаловать!</title>
    <style>
        body { font-family: 'Segoe UI', Arial, sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); margin: 0; padding: 20px; }
        .container { background: white; max-width: 500px; margin: 0 auto; border-radius: 15px; overflow: hidden; box-shadow: 0 10px 30px rgba(0,0,0,0.2); }
        .header { background: #4f46e5; color: white !important; padding: 30px; text-align: center; }
        .content { padding: 30px; }
        .welcome-btn { display: block; background: #10b981; color: white !important; padding: 15px; text-align: center; text-decoration: none; border-radius: 8px; margin: 20px 0; font-weight: bold; }
        .emoji { font-size: 48px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="emoji">🎉</div>
            <h1>Добро пожаловать!</h1>
        </div>
        <div class="content">
            <p>Привет, <strong>{{ username }}</strong>!</p>
            <p>Мы рады видеть вас в {{ service_name }}. Теперь вы можете пользоваться всеми возможностями нашего сервиса.</p>
            <a href="{{ activation_link }}" class="welcome-btn">Активировать аккаунт</a>
            <p style="color: #666 !important; font-size: 14px;">Если кнопка не работает, скопируйте ссылку: {{ activation_link }}</p>
        </div>
    </div>
</body>
</html>""",
            "category_id": 2,  # USER_MANAGEMENT
            "description": "HTML приветственное сообщение для новых пользователей",
        },
    },
    "PASSWORD_RESET": {
        "summary": "Сброс пароля",
        "value": {
            "title": "Восстановление пароля",
            "content": "Здравствуйте, {{ username }}! Для сброса пароля перейдите по ссылке: {{ reset_link }}. Код подтверждения: {{ reset_code }}. Ссылка действительна 24 часа.",
            "category_id": 2,  # USER_MANAGEMENT
            "description": "Восстановление доступа к учетной записи",
        },
    },
    # МЕДИЦИНА (HEALTHCARE)
    "APPOINTMENT_REMINDER": {
        "summary": "Напоминание о приеме",
        "value": {
            "title": "Напоминание о визите к врачу",
            "content": "Уважаемый(ая) {{ patient_name }}! Напоминаем о записи к {{ doctor_name }} завтра в {{ appointment_time }}. Кабинет {{ room_number }}, адрес: {{ clinic_address }}.",
            "category_id": 3,  # HEALTHCARE
            "description": "Напоминание пациентам о предстоящем визите",
        },
    },
    "TEST_RESULTS_HTML": {
        "summary": "Результаты анализов (HTML)",
        "value": {
            "title": "Результаты анализов готовы",
            "content": """<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>Результаты анализов</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; background-color: #f0f8ff; }
        .container { background: white; padding: 25px; border-radius: 10px; border-left: 5px solid #2e8b57; }
        .header { color: #2e8b57 !important; text-align: center; margin-bottom: 20px; }
        .info-block { background: #f0f8ff; padding: 15px; border-radius: 5px; margin: 15px 0; }
        .download-btn { display: inline-block; background: #2e8b57; color: white !important; padding: 10px 20px; text-decoration: none; border-radius: 5px; }
    </style>
</head>
<body>
    <div class="container">
        <h2 class="header">🔬 Результаты анализов</h2>
        <p>Здравствуйте, {{ patient_name }}!</p>
        <div class="info-block">
            <strong>Дата сдачи:</strong> {{ test_date }}<br>
            <strong>Врач:</strong> {{ doctor_name }}
        </div>
        <p>Ваши результаты анализов готовы и доступны для скачивания в личном кабинете.</p>
        <div style="text-align: center;">
            <a href="{{ results_link }}" class="download-btn">Скачать результаты</a>
        </div>
    </div>
</body>
</html>""",
            "category_id": 3,  # HEALTHCARE
            "description": "Уведомление о готовности результатов медицинских анализов",
        },
    },
    # ФИНАНСЫ (FINANCE)
    "PAYMENT_SUCCESS": {
        "summary": "Успешная оплата",
        "value": {
            "title": "Платеж успешно проведен",
            "content": "{{ username }}, ваш платеж на сумму {{ amount }} руб. успешно обработан. Номер операции: {{ transaction_id }}. Остаток на счете: {{ balance }} руб.",
            "category_id": 4,  # FINANCE
            "description": "Подтверждение успешного платежа",
        },
    },
    "LOW_BALANCE_WARNING": {
        "summary": "Низкий баланс",
        "value": {
            "title": "Внимание: низкий баланс",
            "content": "{{ username }}, на вашем счете осталось {{ balance }} руб. Рекомендуем пополнить баланс для избежания блокировки услуг.",
            "category_id": 4,  # FINANCE
            "description": "Предупреждение о низком балансе на счете",
        },
    },
    # МАРКЕТИНГ (MARKETING)
    "BIRTHDAY_SPECIAL_HTML": {
        "summary": "День рождения с подарком (HTML)",
        "value": {
            "title": "🎂 С днем рождения, {{ username }}!",
            "content": """<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>С днем рождения!</title>
    <style>
        body { font-family: Arial, sans-serif; background: linear-gradient(45deg, #ff6b6b, #feca57, #48dbfb, #ff9ff3); margin: 0; padding: 20px; }
        .container { background: white; max-width: 500px; margin: 0 auto; border-radius: 20px; overflow: hidden; text-align: center; box-shadow: 0 15px 35px rgba(0,0,0,0.1); }
        .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white !important; padding: 40px 20px; }
        .content { padding: 30px; }
        .gift-box { font-size: 64px; margin: 20px 0; }
        .promo-code { background: #ffe066; padding: 15px; border-radius: 10px; font-weight: bold; font-size: 18px; margin: 20px 0; }
        .use-btn { display: inline-block; background: #ff6b6b; color: white !important; padding: 15px 30px; text-decoration: none; border-radius: 25px; margin: 20px 0; font-weight: bold; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎉 С ДНЕМ РОЖДЕНИЯ! 🎉</h1>
            <p style="font-size: 18px;">{{ username }}, этот день особенный!</p>
        </div>
        <div class="content">
            <div class="gift-box">🎁</div>
            <p>В честь вашего праздника дарим <strong>{{ discount }}% скидку</strong> на все товары!</p>
            <div class="promo-code">
                Промокод: <strong>{{ promo_code }}</strong>
            </div>
            <a href="{{ shop_link }}" class="use-btn">Использовать подарок</a>
            <p style="color: #666 !important; font-size: 14px;">Скидка действует до {{ expiry_date }}</p>
        </div>
    </div>
</body>
</html>""",
            "category_id": 5,  # MARKETING
            "description": "Праздничное поздравление с персональной скидкой",
        },
    },
    "NEWSLETTER_WEEKLY": {
        "summary": "Еженедельная рассылка",
        "value": {
            "title": "Еженедельный дайджест",
            "content": "Привет, {{ username }}! Новости недели: {{ news_summary }}. Популярные товары: {{ popular_items }}. Специальное предложение: {{ special_offer }}.",
            "category_id": 5,  # MARKETING
            "description": "Еженедельная информационная рассылка",
        },
    },
    # СИСТЕМНЫЕ (SYSTEM)
    "MAINTENANCE_NOTICE": {
        "summary": "Техническое обслуживание",
        "value": {
            "title": "Плановые технические работы",
            "content": "Уважаемые пользователи! {{ maintenance_date }} с {{ start_time }} до {{ end_time }} планируются технические работы. Сервис будет временно недоступен.",
            "category_id": 6,  # SYSTEM
            "description": "Уведомление о плановых технических работах",
        },
    },
    "SECURITY_ALERT_HTML": {
        "summary": "Предупреждение безопасности (HTML)",
        "value": {
            "title": "⚠️ Предупреждение безопасности",
            "content": """<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>Предупреждение безопасности</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; background-color: #fff5f5; }
        .container { background: white; padding: 25px; border-radius: 10px; border-left: 5px solid #dc2626; }
        .warning { background: #fef2f2; color: #dc2626 !important; padding: 15px; border-radius: 5px; text-align: center; margin: 15px 0; }
        .action-required { background: #dc2626; color: white !important; padding: 15px; border-radius: 5px; text-align: center; margin: 20px 0; }
        .secure-btn { display: inline-block; background: #059669; color: white !important; padding: 12px 25px; text-decoration: none; border-radius: 5px; }
    </style>
</head>
<body>
    <div class="container">
        <h2 style="color: #dc2626 !important; text-align: center;">🚨 Предупреждение безопасности</h2>
        <div class="warning">
            <strong>Обнаружена подозрительная активность!</strong>
        </div>
        <p>Здравствуйте, {{ username }}!</p>
        <p>{{ security_date }} в {{ security_time }} был зафиксирован вход в ваш аккаунт с IP-адреса {{ suspicious_ip }}.</p>
        <div class="action-required">
            Если это были не вы - немедленно смените пароль!
        </div>
        <div style="text-align: center;">
            <a href="{{ security_link }}" class="secure-btn">Проверить безопасность</a>
        </div>
    </div>
</body>
</html>""",
            "category_id": 6,  # SYSTEM
            "description": "Критическое уведомление о подозрительной активности",
        },
    },
    "SUBSCRIPTION_EXPIRY": {
        "summary": "Истечение подписки",
        "value": {
            "title": "Подписка истекает",
            "content": "{{ username }}, ваша подписка {{ subscription_type }} истекает {{ expiry_date }}. Для продления перейдите по ссылке {{ renewal_link }}.",
            "category_id": 6,  # SYSTEM
            "description": "Напоминание об истечении срока подписки",
        },
    },
}
