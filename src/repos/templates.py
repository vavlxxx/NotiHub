from sqlalchemy import insert, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload

from src.repos.base import BaseRepository
from src.models.templates import Template, TemplateCategory
from src.schemas.templates import TemplateDTO, TemplateAddDTO, TemplateCategoryDTO
from utils.exceptions import ObjectExistsError


class TemplateRepository(BaseRepository):
    model = Template
    schema = TemplateDTO

    async def add(self, data: TemplateAddDTO, **params):
        add_obj_stmt = (
            insert(self.model).values(**data.model_dump(), **params).returning(self.model)
        )
        try:
            result = await self.session.execute(add_obj_stmt)
        except IntegrityError as exc:
            if isinstance(exc.orig.__cause__, UniqueViolationError):  # type: ignore
                raise ObjectExistsError from exc
            raise exc

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
