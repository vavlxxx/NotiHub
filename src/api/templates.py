from pathlib import Path

from fastapi import APIRouter, Body, Depends

from src.api.examples.templates import EXAMPLE_TEMPLATES
from src.dependencies.db import DBDep
from src.dependencies.users import UserMetaDep, auth_required
from src.dependencies.templates import PaginationDep, TemplateFiltrationDep
from src.schemas.templates import TemplateAddDTO, TemplateUpdateDTO
from src.services.templates import TemplateService

from src.utils.exceptions import (
    TemplateNotFoundError, 
    TemplateNotFoundHTTPError, 
    CategoryNotFoundError, 
    CategoryNotFoundHTTPError
)


router = APIRouter(
    prefix="/templates",
    tags=["Управление шаблонами для уведомлений"]
)


@router.get("/", summary="Получить список всех шаблонов")
async def get_templates_list(
    db: DBDep,
    pagination: PaginationDep,
    template_filtration: TemplateFiltrationDep
):  
    templates = await TemplateService(db).get_templates_list(
        limit=pagination.limit,
        offset=pagination.offset,
        category_id=template_filtration.category_id
    )

    return {
        "page": pagination.page,
        "offset": pagination.offset,
        "data": templates
    }


@router.get("/{template_id}", summary="Получить конкретный шаблон")
async def get_template(
    db: DBDep,
    template_id: int = Path("ID шаблона")
):  
    try:
        template = await TemplateService(db).get_template(template_id=template_id)
    except TemplateNotFoundError as exc:
        raise TemplateNotFoundHTTPError from exc
    
    return {
        "data": template
    }


@router.post("/", summary="Добавить шаблон", dependencies=[Depends(auth_required)])
async def add_template(
    db: DBDep,
    user_meta: UserMetaDep,
    data: TemplateAddDTO = Body(description="Данные о шаблоне", openapi_examples=EXAMPLE_TEMPLATES),
):  
    try:
        template = await TemplateService(db).add_template(data=data)
    except CategoryNotFoundError as exc:
        raise CategoryNotFoundHTTPError from exc
    
    return {
        "data": template
    }


@router.patch("/{template_id}", summary="Обновить шаблон", dependencies=[Depends(auth_required)])
async def update_template(
    db: DBDep,
    data: TemplateUpdateDTO,
    user_meta: UserMetaDep,
    template_id: int = Path()
):  
    try:
        await TemplateService(db).update_template(template_id=template_id, data=data)
    except TemplateNotFoundError as exc:
        raise TemplateNotFoundHTTPError from exc
    except CategoryNotFoundError as exc:
        raise CategoryNotFoundHTTPError from exc
    
    return {"status": "OK"}


@router.delete("/{template_id}", summary="Удалить шаблон", dependencies=[Depends(auth_required)])
async def delete_template(
    db: DBDep,
    user_meta: UserMetaDep,
    template_id: int = Path()
):
    try:
        await TemplateService(db).delete_template(template_id=template_id)
    except TemplateNotFoundError as exc:
        raise TemplateNotFoundHTTPError from exc
    
    return {"status": "OK"}


