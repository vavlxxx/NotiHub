from src.services.base import BaseService
from src.schemas.templates import TemplateAddDTO, TemplateCategoryAddDTO, TemplateDTO
from src.utils.exceptions import ObjectNotFoundError, TemplateNotFoundError, TemplateCategoryNotFoundError


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
            category_id=category_id,
            is_active=True
        )

    async def add_template(self, data: TemplateAddDTO) -> dict:
        if not hasattr(data, 'category_id') or data.category_id is None:
            category_data = TemplateCategoryAddDTO(
                title='Без категории', 
                description='Категория по умолчанию',
                parent_id=None
            )
            default_category = await self.db.template_categories.get_one_or_add(category_data)
            data.category_id = default_category.id
        else:
            try:
                await self.db.template_categories.get_one(id=data.category_id)
            except ObjectNotFoundError as exc:
                raise TemplateCategoryNotFoundError from exc
            
        template = await self.db.templates.add(data)
        await self.db.commit()
        return template

    async def update_template(self, data: TemplateAddDTO, template_id: int) -> TemplateAddDTO:
        if data.category_id is not None:
            try:
                await self.db.template_categories.get_one(id=data.category_id)
            except ObjectNotFoundError as exc:
                raise TemplateCategoryNotFoundError from exc
        
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
        