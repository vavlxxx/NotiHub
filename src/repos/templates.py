from sqlalchemy import insert, select
from sqlalchemy.orm import joinedload

from src.repos.base import BaseRepository
from src.models.templates import Template, TemplateCategory
from src.schemas.templates import TemplateDTO, TemplateAddDTO, TemplateCategoryDTO


class TemplateRepository(BaseRepository):
    model = Template
    schema = TemplateDTO

    async def add(self, data: TemplateAddDTO, **params):
        add_obj_stmt = (
            insert(self.model)
            .values(**data.model_dump(), **params)
            .returning(self.model)
        )
        result = await self.session.execute(add_obj_stmt)

        obj = result.scalars().one()
        query = (
            select(self.model)
            .filter_by(id=obj.id)
            .options(joinedload(Template.category))
        )
        result = await self.session.execute(query)
        return self.schema.model_validate(result.scalars().one())


class TemplateCategoryRepository(BaseRepository):
    model = TemplateCategory
    schema = TemplateCategoryDTO
