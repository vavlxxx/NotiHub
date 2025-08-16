from schemas.templates import TemplateDTO
from src.services.base import BaseService
from src.schemas.categories import AddCategoryDTO, CategoryDTO

from src.utils.exceptions import (
    CategoryInUseError,
    ObjectExistsError,
    ObjectNotFoundError,
    CategoryExistsError,
    CategoryNotFoundError
)


class CategoryService(BaseService):
    async def get_categories_list(self) -> list[CategoryDTO]:
        categories: list[CategoryDTO] = await self.db.categories.get_all_filtered()
        return categories
    

    async def add_category(self, data: AddCategoryDTO) -> CategoryDTO:
        if hasattr(data, 'parent_id') and data.parent_id is not None:
            try:
                await self.db.categories.get_one(id=data.parent_id)
            except ObjectNotFoundError as exc:
                raise CategoryNotFoundError from exc

        try:
            category: CategoryDTO = await self.db.categories.add(data)
        except ObjectExistsError as exc:
            raise CategoryExistsError from exc
        await self.db.commit()
        return category
    

    async def update_category(self, data: AddCategoryDTO, category_id: int) -> None:
        if hasattr(data, 'parent_id') and data.parent_id is not None:
            try:
                await self.db.categories.get_one(id=data.parent_id)
            except ObjectNotFoundError as exc:
                raise CategoryNotFoundError from exc

        try:
            await self.db.categories.edit(data=data, id=category_id)
        except ObjectNotFoundError as exc:
            raise CategoryNotFoundError from exc
        except ObjectExistsError as exc:
            raise CategoryExistsError from exc
        await self.db.commit()


    async def delete_category(self, category_id: int) -> None:
        templates: list[TemplateDTO] = await self.db.templates.get_all_filtered(category_id=category_id)
        if templates:
            raise CategoryInUseError(
                detail="Данная категория используется в шаблонах с id: " + 
                ', '.join(map(str, [template.id for template in templates]))
            )
        
        try:
            await self.db.categories.delete(id=category_id)
        except ObjectNotFoundError as exc:
            raise CategoryNotFoundError from exc
        await self.db.commit()
