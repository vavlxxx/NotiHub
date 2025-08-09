from sqlalchemy import select

from src.repos.base import BaseRepository
from src.models.templates import Category
from src.schemas.categories import CategoryDTO


class CategoryRepository(BaseRepository):
    model = Category
    schema = CategoryDTO

    async def get_all_filtered_with_params(self, limit: int, offset: int, **filter_by):
        query = (
            select(self.model)
            .filter_by(**filter_by)
            .limit(limit)
            .offset(offset) 
        )
        result = await self.session.execute(query)
        return [self.schema.model_validate(obj) for obj in result.scalars().all()]
    