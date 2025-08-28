from jinja2 import TemplateSyntaxError

from src.settings import settings
from src.services.base import BaseService
from src.schemas.templates import (
    AddTemplateDTO,
    RequestAddTemplateDTO,
    TemplateDTO,
    TemplateUpdateDTO,
)
from src.schemas.categories import AddCategoryDTO, CategoryDTO
from src.utils.exceptions import (
    ObjectExistsError,
    ObjectNotFoundError,
    TemplateNotFoundError,
    CategoryNotFoundError,
    TemplateExistsError,
    TemplateSyntaxCheckError,
)


class TemplateService(BaseService):
    async def get_templates_list(
        self,
        limit: int,
        offset: int,
        category_id: int | None,
        only_mine: bool,
        user_meta: dict,
    ) -> tuple[int, list[TemplateDTO]]:
        (
            total_count,
            templates,
        ) = await self.db.templates.get_all_filtered_with_pagination(
            limit=limit,
            offset=offset,
            category_id=category_id,
            user_id=user_meta.get("user_id", 0) if only_mine else None,
        )
        return total_count, templates

    async def get_template(self, template_id: int) -> TemplateDTO:
        try:
            template: TemplateDTO = await self.db.templates.get_one(id=template_id)
        except ObjectNotFoundError as exc:
            raise TemplateNotFoundError from exc
        return template

    async def _validate_template(
        self, template: RequestAddTemplateDTO | TemplateUpdateDTO
    ) -> None:
        if template.content is None:
            return

        try:
            settings.JINGA2_ENV.from_string(template.content)
        except TemplateSyntaxError as exc:
            raise TemplateSyntaxCheckError from exc

    async def add_template(
        self, data: RequestAddTemplateDTO, user_meta: dict
    ) -> TemplateDTO:
        await self._validate_template(data)
        if not hasattr(data, "category_id") or data.category_id is None:
            default_category: CategoryDTO = await self.db.categories.get_one_or_add(
                AddCategoryDTO(
                    title="Без категории",
                    description="Категория по умолчанию",
                    parent_id=None,
                )
            )
            data.category_id = default_category.id
        else:
            try:
                await self.db.categories.get_one(id=data.category_id)
            except ObjectNotFoundError as exc:
                raise CategoryNotFoundError from exc

        new_template_schema = AddTemplateDTO(
            **data.model_dump(), user_id=user_meta.get("user_id", 0)
        )

        try:
            template: TemplateDTO = await self.db.templates.add(new_template_schema)
        except ObjectExistsError as exc:
            raise TemplateExistsError from exc

        await self.db.commit()
        return template

    async def update_template(
        self, data: TemplateUpdateDTO, template_id: int, user_meta: dict
    ) -> None:
        if data.content is not None:
            await self._validate_template(data)
        if data.category_id is not None:
            try:
                await self.db.categories.get_one(id=data.category_id)
            except ObjectNotFoundError as exc:
                raise CategoryNotFoundError from exc

        try:
            await self.db.templates.edit(
                user_id=user_meta.get("user_id", 0),
                id=template_id,
                data=data,
            )
        except ObjectNotFoundError as exc:
            raise TemplateNotFoundError from exc
        await self.db.commit()

    async def delete_template(self, template_id: int, user_meta: dict) -> None:
        try:
            await self.db.templates.delete(
                user_id=user_meta.get("user_id", 0), id=template_id
            )
        except ObjectNotFoundError as exc:
            raise TemplateNotFoundError from exc
        await self.db.commit()
