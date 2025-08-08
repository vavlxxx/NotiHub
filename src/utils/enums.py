from enum import Enum

class ContactChannelType(str, Enum):
    EMAIL = "EMAIL"
    TELEGRAM = "TELEGRAM"

class UserRole(str, Enum):
    ADMIN = "ADMIN"
    USER = "USER"
