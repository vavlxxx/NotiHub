from sqlalchemy import select
from sqlalchemy import func
from sqlalchemy.exc import DBAPIError
from asyncpg import DataError

from src.repos.base import BaseRepository
from src.models.templates import Template
from src.schemas.templates import TemplateDTO
from src.utils.exceptions import ValueOutOfRangeError


class TemplateRepository(BaseRepository):
    model = Template
    schema = TemplateDTO

    async def get_all_filtered_with_pagination(
        self, limit: int, offset: int, **filter_by
    ) -> tuple[int, list[TemplateDTO]]:
        if filter_by.get("category_id") is None:
            del filter_by["category_id"]
        if filter_by.get("user_id") is None:
            del filter_by["user_id"]

        total_count_subquery = (
            select(func.count())
            .select_from(self.model)
            .filter_by(**filter_by)
            .scalar_subquery()
        )

        query = (
            select(self.model, total_count_subquery.label("total_count"))
            .filter_by(**filter_by)
            .order_by(self.model.id.asc())
        )

        query = query.limit(limit).offset(offset)
        try:
            result = await self.session.execute(query)
        except DBAPIError as exc:
            if isinstance(exc.orig.__cause__, DataError):  # type: ignore
                raise ValueOutOfRangeError(detail=exc.orig.__cause__.args[0]) from exc  # type: ignore
            raise exc

        rows = result.fetchall()

        if not rows:
            total_count_result = await self.session.execute(
                select(func.count()).select_from(self.model).filter_by(**filter_by)
            )
            total_count = total_count_result.scalar() or 0
            return total_count, []

        total_count = rows[0].total_count
        templates: list[TemplateDTO] = [
            self.schema.model_validate(row[0]) for row in rows
        ]

        return total_count, templates
