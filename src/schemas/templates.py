from datetime import datetime
from src.schemas.base import BaseDTO


class TemplateCategoryAddDTO(BaseDTO):
    title: str
    description: str | None = None
    parent_id: int | None = None

class TemplateCategoryDTO(TemplateCategoryAddDTO):
    id: int

class TemplateCategoryUpdateDTO(TemplateCategoryAddDTO):
    title: str | None = None
    description: str | None = None
    parent_id: int | None = None


class TemplateAddDTO(BaseDTO):
    title: str
    content: str
    category_id: int | None = None
    description: str | None = None

class TemplateUpdateDTO(BaseDTO):
    title: str | None = None
    content: str | None = None
    category_id: int | None = None
    description: str | None = None
    is_active: bool | None = None

class TemplateDTO(BaseDTO):
    id: int
    title: str
    content: str
    description: str | None
    category_id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
