import math
from pathlib import Path

from fastapi import APIRouter, Body, Depends
from fastapi_cache.decorator import cache

from src.api.examples.templates import EXAMPLE_TEMPLATES
from src.dependencies.db import DBDep
from src.dependencies.users import UserMetaDep, auth_required
from src.dependencies.templates import TemplateFiltrationDep
from src.dependencies.pagination import PaginationDep
from src.schemas.templates import RequestAddTemplateDTO, TemplateUpdateDTO
from src.services.templates import TemplateService
from src.utils.exceptions import (
    TemplateExistsError,
    TemplateExistsHTTPError,
    TemplateNotFoundError, 
    TemplateNotFoundHTTPError, 
    CategoryNotFoundError, 
    CategoryNotFoundHTTPError,
    TemplateSyntaxCheckError,
    TemplateSyntaxCheckHTTPError,
    ValueOutOfRangeError,
    ValueOutOfRangeHTTPError
)


router = APIRouter(
    prefix="/templates",
    tags=["Управление шаблонами для уведомлений"]
)


@router.get("", summary="Получить список всех шаблонов", dependencies=[Depends(auth_required)])
@cache(expire=120)
async def get_templates_list(
    db: DBDep,
    pagination: PaginationDep,
    user_meta: UserMetaDep,
    template_filtration: TemplateFiltrationDep
):  
    total_count, templates = await TemplateService(db).get_templates_list(
        limit=pagination.limit,
        offset=pagination.offset,
        category_id=template_filtration.category_id,
        user_meta=user_meta,
        only_mine=template_filtration.only_mine
    )

    return {
        "page": pagination.page,
        "per_page": pagination.limit,
        "total_count": total_count,
        "total_pages": math.ceil(total_count / pagination.limit),
        "offset": pagination.offset,
        "data": templates
    }


@router.get("/{template_id}", summary="Получить конкретный шаблон по ID")
async def get_template(
    db: DBDep,
    template_id: int = Path(description="ID шаблона") # type: ignore
):  
    try:
        template = await TemplateService(db).get_template(template_id=template_id)
    except TemplateNotFoundError as exc:
        raise TemplateNotFoundHTTPError from exc
    except ValueOutOfRangeError as exc:
        raise ValueOutOfRangeHTTPError(detail=exc.detail) from exc
    
    return {
        "status": "OK",
        "data": template
    }


@router.post("", summary="Добавить шаблон", dependencies=[Depends(auth_required)])
async def add_template(
    db: DBDep,
    user_meta: UserMetaDep,
    data: RequestAddTemplateDTO = Body(description="Данные о шаблоне", openapi_examples=EXAMPLE_TEMPLATES),
):  
    try:
        template = await TemplateService(db).add_template(data=data, user_meta=user_meta)
    except CategoryNotFoundError as exc:
        raise CategoryNotFoundHTTPError from exc
    except TemplateSyntaxCheckError as exc:
        raise TemplateSyntaxCheckHTTPError from exc
    except TemplateExistsError as exc:
        raise TemplateExistsHTTPError from exc
    return {
        "status": "OK",
        "data": template
    }


@router.patch("/{template_id}", summary="Обновить шаблон", dependencies=[Depends(auth_required)])
async def update_template(
    db: DBDep,
    user_meta: UserMetaDep,
    template_id: int = Path(description="ID шаблона"), # type: ignore
    data: TemplateUpdateDTO = Body(description="Данные о шаблоне", openapi_examples=EXAMPLE_TEMPLATES)
):  
    try:
        await TemplateService(db).update_template(
            template_id=template_id, 
            user_meta=user_meta,
            data=data
        )
    except TemplateNotFoundError as exc:
        raise TemplateNotFoundHTTPError from exc
    except CategoryNotFoundError as exc:
        raise CategoryNotFoundHTTPError from exc
    except TemplateSyntaxCheckError as exc:
        raise TemplateSyntaxCheckHTTPError from exc
    except ValueOutOfRangeError as exc:
        raise ValueOutOfRangeHTTPError(detail=exc.detail) from exc
    return {"status": "OK"}


@router.delete("/{template_id}", summary="Удалить шаблон", dependencies=[Depends(auth_required)])
async def delete_template(
    db: DBDep,
    user_meta: UserMetaDep,
    template_id: int = Path(description="ID шаблона") # type: ignore
):
    try:
        await TemplateService(db).delete_template(
            template_id=template_id,
            user_meta=user_meta
        )
    except TemplateNotFoundError as exc:
        raise TemplateNotFoundHTTPError from exc
    except ValueOutOfRangeError as exc:
        raise ValueOutOfRangeHTTPError(detail=exc.detail) from exc
    return {"status": "OK"}
