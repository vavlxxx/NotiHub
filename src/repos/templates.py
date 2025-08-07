from sqlalchemy import insert, select
from sqlalchemy.orm import joinedload

from src.repos.base import BaseRepository
from src.models.templates import Template, TemplateCategory
from src.schemas.templates import TemplateDTO, TemplateAddDTO, TemplateCategoryDTO


class TemplateRepository(BaseRepository):
    model = Template
    schema = TemplateDTO

    async def get_all_filtered_with_params(self, limit: int, offset: int, category_id: int | None, **filter_by):
        query = (
            select(self.model)
            .filter_by(**filter_by)
        )
        if category_id:
            query = query.filter_by(category_id=category_id)

        query = query.limit(limit).offset(offset) 
        result = await self.session.execute(query)

        return [self.schema.model_validate(obj) for obj in result.scalars().all()]


class TemplateCategoryRepository(BaseRepository):
    model = TemplateCategory
    schema = TemplateCategoryDTO
