from src.services.base import BaseService
from src.schemas.templates import TemplateAddDTO
from src.schemas.categories import CategoryAddDTO, CategoryDTO

from src.utils.exceptions import (
    ObjectExistsError,
    ObjectNotFoundError,
    CategoryExistsError,
    CategoryNotFoundError
)


class CategoryService(BaseService):
    
    async def get_categories_list(self, limit: int, offset: int) -> list[CategoryDTO]:
        return await self.db.categories.get_all_filtered_with_params(
            limit=limit, 
            offset=offset
        )
    

    async def add_category(self, data: CategoryAddDTO) -> CategoryDTO:
        if hasattr(data, 'parent_id') and data.parent_id is not None:
            try:
                await self.db.categories.get_one(id=data.parent_id)
            except ObjectNotFoundError as exc:
                raise CategoryNotFoundError from exc

        try:
            category = await self.db.categories.add(data)
        except ObjectExistsError as exc:
            raise CategoryExistsError from exc
        
        await self.db.commit()
        return category
    

    async def update_category(self, data: TemplateAddDTO, category_id: int) -> TemplateAddDTO:
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
        try:
            await self.db.categories.delete(id=category_id)
        except ObjectNotFoundError as exc:
            raise CategoryNotFoundError from exc
        await self.db.commit()
