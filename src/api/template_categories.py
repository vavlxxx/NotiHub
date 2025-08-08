# from pathlib import Path

# from fastapi import APIRouter, Body

# from src.api.examples.templates import EXAMPLE_TEMPLATES
# from src.dependencies.db import DBDep
# from src.dependencies.templates import PaginationDep, TemplateFiltrationDep
# from src.schemas.templates import TemplateAddDTO
# from src.services.templates import TemplateCategoryService
# from src.utils.exceptions import (
#     TemplateNotFoundError, 
#     TemplateNotFoundHTTPError, 
#     TemplateCategoryNotFoundError, 
#     TemplateCategoryNotFoundHTTPError
# )


# router = APIRouter(
#     prefix="/templates",
#     tags=["Шаблоны для уведомлений"]
# )


# @router.get("/", summary="Получить список всех шаблонов")
# async def get_templates_list(
#     db: DBDep,
#     pagination: PaginationDep,
#     template_filtration: TemplateFiltrationDep
# ):  
#     templates = await TemplateCategoryService(db).get_templates_list(
#         limit=pagination.limit,
#         offset=pagination.offset,
#         category_id=template_filtration.category_id
#     )

#     return {
#         "page": pagination.page,
#         "offset": pagination.offset,
#         "data": templates
#     }


# @router.get("/{template_id}", summary="Получить конкретный шаблон")
# async def get_template(
#     db: DBDep,
#     template_id: int = Path("ID шаблона")
# ):  
#     try:
#         template = await TemplateCategoryService(db).get_template(template_id=template_id)
#     except TemplateNotFoundError as exc:
#         raise TemplateNotFoundHTTPError from exc
    
#     return {
#         "data": template
#     }


# @router.post("/", summary="Добавить шаблон")
# async def add_template(
#     db: DBDep,
#     data: TemplateAddDTO = Body(description="Данные о шаблоне", openapi_examples=EXAMPLE_TEMPLATES),
# ):  
#     try:
#         template = await TemplateCategoryService(db).add_template(data=data)
#     except TemplateCategoryNotFoundError as exc:
#         raise TemplateCategoryNotFoundHTTPError from exc
    
#     return {
#         "data": template
#     }


# @router.patch("/{template_id}", summary="Обновить шаблон")
# async def update_template(
#     db: DBDep,
#     data: TemplateAddDTO,
#     template_id: int = Path()
# ):  
#     try:
#         await TemplateCategoryService(db).update_template(template_id=template_id, data=data)
#     except TemplateNotFoundError as exc:
#         raise TemplateNotFoundHTTPError from exc
#     except TemplateCategoryNotFoundError as exc:
#         raise TemplateCategoryNotFoundHTTPError from exc
    
#     return {"status": "OK"}


# @router.delete("/{template_id}", summary="Удалить шаблон")
# async def delete_template(
#     db: DBDep,
#     template_id: int = Path()
# ):
#     try:
#         await TemplateCategoryService(db).delete_template(template_id=template_id)
#     except TemplateNotFoundError as exc:
#         raise TemplateNotFoundHTTPError from exc
    
#     return {"status": "OK"}


