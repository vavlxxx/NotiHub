from src.schemas.base import BaseDTO

class CategoryAddDTO(BaseDTO):
    title: str
    description: str | None = None
    parent_id: int | None = None

class CategoryDTO(CategoryAddDTO):
    id: int

class CategoryUpdateDTO(CategoryAddDTO):
    title: str | None = None
    description: str | None = None
    parent_id: int | None = None