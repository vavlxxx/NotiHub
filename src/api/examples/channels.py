from typing import Dict
from fastapi.openapi.models import Example


EXAMPLE_CHANNELS: Dict[str, Example] = {
    "TELEGRAM": {
        "summary": "TELEGRAM",
        "value": {
            "contact_value": "your_telegram_id",
            "channel_type": "TELEGRAM"
        }
    },
    
    "EMAIL": {
        "summary": "EMAIL",
        "value": {
            "contact_value": "your_email",
            "channel_type": "EMAIL"
        }
    },
}
