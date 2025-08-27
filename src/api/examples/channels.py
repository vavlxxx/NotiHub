from typing import Dict
from fastapi.openapi.models import Example


EXAMPLE_CHANNELS: Dict[str, Example] = {
    "TELEGRAM": {
        "summary": "TELEGRAM",
        "value": {"contact_value": "telegram_id/username", "channel_type": "TELEGRAM"},
    },
    "EMAIL": {
        "summary": "EMAIL",
        "value": {"contact_value": "email", "channel_type": "EMAIL"},
    },
    "PUSH": {
        "summary": "PUSH",
        "value": {"contact_value": "topic_from_ntfy", "channel_type": "PUSH"},
    },
}
