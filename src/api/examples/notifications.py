from typing import Dict
from fastapi.openapi.models import Example


EXAMPLE_NOTIFICATIONS: Dict[str, Example] = {
    "DEFAULT": {
        "summary": "Обычное уведомление",
        "value": {
            "schedule_type": "ONCE",
            "template_id": 1,
            "channels_ids": [ 1 ],
            "variables": { 
                "key": "value", 
            }
        }
    },
    "DEFAULT_SCHEDULED": {
        "summary": "Обычное запланированное уведомление",
        "value": {
            "schedule_type": "ONCE",
            "scheduled_at": "2023-01-01 00:00:00",
            "template_id": 1,
            "channels_ids": [ 1 ],
            "variables": { 
                "key": "value", 
            }
        }
    },
    "RECURRING": {
        "summary": "Периодическое уведомление",
        "value": {
            "schedule_type": "RECURRING",
            "template_id": 1,
            "channels_ids": [ 1 ],
            "crontab": "* * * * *",
            "variables": { 
                "key": "value", 
            }
        }
    },
    "RECURRING_EXTRA": {
        "summary": "Периодическое уведомление (с доп. параметрами)",
        "value": {
            "schedule_type": "RECURRING",
            "template_id": 1,
            "max_executions": 5,
            "scheduled_at": "2023-01-01 00:00:00",
            "channels_ids": [ 1 ],
            "crontab": "* * * * *",
            "variables": { 
                "key": "value", 
            }
        }
    },
}


EXAMPLE_NOTIFICATIONS_FOR_ALL: Dict[str, Example] = {
    "DEFAULT": {
        "summary": "Обычное уведомление",
        "value": {
            "schedule_type": "ONCE",
            "template_id": 1,
            "variables": { 
                "key": "value", 
            }
        }
    },
    "DEFAULT_SCHEDULED": {
        "summary": "Обычное запланированное уведомление",
        "value": {
            "schedule_type": "ONCE",
            "scheduled_at": "2023-01-01 00:00:00",
            "template_id": 1,
            "variables": { 
                "key": "value", 
            }
        }
    },
    "RECURRING": {
        "summary": "Периодическое уведомление",
        "value": {
            "schedule_type": "RECURRING",
            "template_id": 1,
            "crontab": "* * * * *",
            "variables": { 
                "key": "value", 
            }
        }
    },
    "RECURRING_EXTRA": {
        "summary": "Периодическое уведомление (с доп. параметрами)",
        "value": {
            "schedule_type": "RECURRING",
            "template_id": 1,
            "max_executions": 5,
            "scheduled_at": "2023-01-01 00:00:00",
            "crontab": "* * * * *",
            "variables": { 
                "key": "value", 
            }
        }
    },
}
