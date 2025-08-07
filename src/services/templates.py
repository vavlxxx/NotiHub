from src.services.base import BaseService
from src.schemas.templates import TemplateAddDTO, TemplateCategoryAddDTO


class TemplateService(BaseService):
    
    async def add_template(self, data: TemplateAddDTO) -> dict:
        if not hasattr(data, 'category_id') or data.category_id is None:
            category_data = TemplateCategoryAddDTO(
                title='Без категории', 
                description='Категория по умолчанию',
                parent_id=None
            )
            default_category = await self.db.template_categories.get_one_or_add(category_data)
            data.category_id = default_category.id
            
        template = await self.db.templates.add(data)
        await self.db.commit()
        return template
