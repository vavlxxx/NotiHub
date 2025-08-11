from jinja2 import TemplateSyntaxError
import settings
from src.services.base import BaseService
from src.schemas.templates import TemplateAddDTO, TemplateDTO, TemplateUpdateDTO
from src.schemas.categories import CategoryAddDTO
from src.utils.exceptions import (
    ObjectNotFoundError,
    TemplateNotFoundError, 
    CategoryNotFoundError,
    TemplateSyntaxCheckError
)


class TemplateService(BaseService):
    
    async def get_template(self, template_id: int) -> TemplateDTO:
        try:
            return await self.db.templates.get_one(id=template_id, is_active=True)
        except ObjectNotFoundError as exc:
            raise TemplateNotFoundError from exc


    async def get_templates_list(self, limit: int, offset: int, category_id: int | None) -> list[TemplateDTO]:
        return await self.db.templates.get_all_filtered_with_params(
            limit=limit, 
            offset=offset,
            category_id=category_id
        )

    
    async def _validate_template(self, template: TemplateAddDTO | TemplateUpdateDTO) -> None:
        try:
            settings.JINGA2_ENV.from_string(template.content)
        except TemplateSyntaxError as exc:
            raise TemplateSyntaxCheckError from exc


    async def add_template(self, data: TemplateAddDTO) -> dict:
        await self._validate_template(data)
        if not hasattr(data, 'category_id') or data.category_id is None:
            default_category = await self.db.categories.get_one_or_add(
                CategoryAddDTO(
                    title='Без категории', 
                    description='Категория по умолчанию',
                    parent_id=None
                )
            )
            data.category_id = default_category.id
        else:
            try:
                await self.db.categories.get_one(id=data.category_id)
            except ObjectNotFoundError as exc:
                raise CategoryNotFoundError from exc
        
        template = await self.db.templates.add(data)
        await self.db.commit()
        return template


    async def update_template(self, data: TemplateUpdateDTO, template_id: int):

        if data.content is not None:
            await self._validate_template(data)

        if data.category_id is not None:
            try:
                await self.db.categories.get_one(id=data.category_id)
            except ObjectNotFoundError as exc:
                raise CategoryNotFoundError from exc
        
        try:
            await self.db.templates.edit(data=data, id=template_id)
            await self.db.commit()
        except ObjectNotFoundError as exc:
            raise TemplateNotFoundError from exc
        

    async def delete_template(self, template_id: int) -> None:
        try:
            await self.db.templates.delete(id=template_id)
            await self.db.commit()
        except ObjectNotFoundError as exc:
            raise TemplateNotFoundError from exc
