from typing import Annotated

from fastapi import Depends, Query
from jinja2.exceptions import TemplateSyntaxError

from src.schemas.templates import TemplateAddDTO, TemplateUpdateDTO
from src.schemas.base import BaseDTO
from src.settings import environment
from src.utils.exceptions import TemplateSyntaxHTTPError


class PaginationParamsDTO(BaseDTO):
    page: Annotated[int, Query(1, ge=1)]
    limit: Annotated[int, Query(None, ge=1, le=15)]

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.limit

def get_pagination_params(
    page: Annotated[int, Query(ge=1, description="Номер страницы")] = 1,
    limit: Annotated[int, Query(ge=1, le=15, description="Максимальное количество шаблонов на одной странице")] = 15,
) -> PaginationParamsDTO:
    return PaginationParamsDTO(page=page, limit=limit)

PaginationDep = Annotated[PaginationParamsDTO, Depends(get_pagination_params)]


class TemplateFiltrationDTO(BaseDTO):
    category_id: int | None

def get_templates_filtration_params(
    category_id: Annotated[int | None, Query(description="ID категории шаблона")] = None
) -> TemplateFiltrationDTO:
    return TemplateFiltrationDTO(category_id=category_id)

TemplateFiltrationDep = Annotated[TemplateFiltrationDTO, Depends(get_templates_filtration_params)]


# def check_template_validity(schema: TemplateAddDTO | TemplateUpdateDTO) -> None:
#     try:
#         environment.from_string(f"{schema.title}\n\n{schema.content}")
#     except TemplateSyntaxError as exc:
#         raise TemplateSyntaxHTTPError from exc
#     return schema

# ValidTemplateDep = Annotated[TemplateAddDTO, Depends(check_template_validity)]
