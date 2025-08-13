from sqlalchemy import select

from src.repos.base import BaseRepository
from src.models.templates import Template
from src.schemas.templates import TemplateDTO


class TemplateRepository(BaseRepository):
    model = Template
    schema = TemplateDTO

    async def get_all_filtered_with_params(
            self, 
            limit: int, 
            offset: int, 
            category_id: int | None, 
            user_id: int | None,
            **filter_by):
        
        query = (select(self.model).filter_by(**filter_by))

        if category_id:
            query = query.filter_by(category_id=category_id)
        if user_id:
            query = query.filter_by(owner_id=user_id)

        query = query.limit(limit).offset(offset) 
        result = await self.session.execute(query)

        return [self.schema.model_validate(obj) for obj in result.scalars().all()]
    