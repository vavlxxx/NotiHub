from enum import Enum


class ContactChannelType(str, Enum):
    EMAIL = "EMAIL"
    TELEGRAM = "TELEGRAM"
    PUSH = "PUSH"


class UserRole(str, Enum):
    ADMIN = "ADMIN"
    USER = "USER"


class NotificationStatus(str, Enum):
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"


class ScheduleType(str, Enum):
    ONCE = "ONCE"
    RECURRING = "RECURRING"


class ContentType(str, Enum):
    PLAIN = "plain"
    HTML = "html"
