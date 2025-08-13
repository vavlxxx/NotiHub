from datetime import datetime
from src.schemas.base import BaseDTO


class RequestAddTemplateDTO(BaseDTO):
    title: str
    content: str
    category_id: int | None = None
    description: str | None = None

class AddTemplateDTO(RequestAddTemplateDTO):
    owner_id: int

class TemplateUpdateDTO(BaseDTO):
    title: str | None = None
    content: str | None = None
    category_id: int | None = None
    description: str | None = None

class TemplateDTO(BaseDTO):
    id: int
    title: str
    content: str
    description: str | None
    category_id: int
    created_at: datetime
    updated_at: datetime
