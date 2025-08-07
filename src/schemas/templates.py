from datetime import datetime
from pydantic import model_validator
from jinja2 import Template
from src.schemas.base import BaseDTO


class TemplateCategoryAddDTO(BaseDTO):
    title: str
    description: str
    parent_id: int | None

class TemplateCategoryDTO(TemplateCategoryAddDTO):
    id: int


class TemplateAddDTO(BaseDTO):
    title: str
    content: str
    category_id: int | None = None
    description: str | None = None

    @model_validator(mode='after')
    @classmethod
    def validate_category_id(cls, instance):
        Template(instance.content)
        Template(instance.title)
        return instance

class TemplateDTO(BaseDTO):
    id: int
    title: str
    content: str
    description: str | None
    category: TemplateCategoryDTO
    is_active: bool
    created_at: datetime
    updated_at: datetime
