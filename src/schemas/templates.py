from datetime import datetime
from pydantic import model_validator
from src.schemas.base import BaseDTO


class RequestAddTemplateDTO(BaseDTO):
    title: str
    content: str
    category_id: int | None = None
    description: str | None = None


class AddTemplateDTO(RequestAddTemplateDTO):
    user_id: int


class TemplateUpdateDTO(BaseDTO):
    title: str | None = None
    content: str | None = None
    category_id: int | None = None
    description: str | None = None

    @model_validator(mode="after")
    def validate_all_fields_are_providen(self):
        values = tuple(self.model_dump().values())
        if all(map(lambda val: val is None, values)):
            raise ValueError("provide at least one non-empty field")
        return self


class TemplateDTO(BaseDTO):
    id: int
    title: str
    content: str
    description: str | None
    category_id: int
    created_at: datetime
    updated_at: datetime
