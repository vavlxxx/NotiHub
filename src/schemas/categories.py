from pydantic import model_validator
from src.schemas.base import BaseDTO

class AddCategoryDTO(BaseDTO):
    title: str
    description: str | None = None
    parent_id: int | None = None

class CategoryDTO(AddCategoryDTO):
    id: int

class UpdateCategoryDTO(AddCategoryDTO):
    title: str | None = None
    description: str | None = None
    parent_id: int | None = None

    @model_validator(mode="after")
    def validate_all_fields_are_providen(self):
        values = tuple(self.model_dump().values())
        if all(map(lambda val: val is None, values)):
            raise ValueError("provide at least one non-empty field")
        return self
    