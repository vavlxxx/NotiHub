from src.repos.base import BaseRepository
from src.models.templates import Category
from src.schemas.categories import CategoryDTO


class CategoryRepository(BaseRepository):
    model = Category
    schema = CategoryDTO
