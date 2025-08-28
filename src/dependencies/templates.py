from typing import Annotated

from fastapi import Depends, Query

from src.schemas.base import BaseDTO


class TemplateFiltrationDTO(BaseDTO):
    category_id: int | None
    only_mine: bool


def get_templates_filtration_params(
    category_id: Annotated[
        int | None, Query(description="ID категории шаблона")
    ] = None,
    only_mine: Annotated[
        bool, Query(description="Показывать только мои шаблоны")
    ] = False,
) -> TemplateFiltrationDTO:
    return TemplateFiltrationDTO(category_id=category_id, only_mine=only_mine)


TemplateFiltrationDep = Annotated[
    TemplateFiltrationDTO, Depends(get_templates_filtration_params)
]
