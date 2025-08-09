from pathlib import Path

from fastapi import APIRouter, Body, Depends

from src.dependencies.db import DBDep
from src.dependencies.templates import PaginationDep
from src.dependencies.users import only_staff
from src.schemas.categories import CategoryAddDTO, CategoryUpdateDTO
from src.services.categories import CategoryService
from src.utils.exceptions import (
    CategoryExistsError,
    CategoryExistsHTTPError,
    CategoryNotFoundError, 
    CategoryNotFoundHTTPError
)


router = APIRouter(
    prefix="/categories",
    tags=["Категории шаблонов уведомлений"]
)


@router.get("/", summary="Получить список всех категорий для шаблонов")
async def get_categories_list(
    db: DBDep,
    pagination: PaginationDep,
):  
    categories = await CategoryService(db).get_categories_list(
        limit=pagination.limit,
        offset=pagination.offset
    )

    return {
        "page": pagination.page,
        "offset": pagination.offset,
        "data": categories
    }


@router.post(
        path="/", 
        summary="Добавить новую категорию | Только для персонала", 
        dependencies=[Depends(only_staff)])
async def add_category(
    db: DBDep,
    data: CategoryAddDTO = Body(description="Данные о категории"),
):  
    try:
        category = await CategoryService(db).add_category(data=data)
    except CategoryNotFoundError as exc:
        raise CategoryNotFoundHTTPError from exc
    except CategoryExistsError as exc:
        raise CategoryExistsHTTPError from exc
    
    return {
        "data": category
    }


@router.patch(
        path="/{category_id}", 
        summary="Обновить категорию шаблона | Только для персонала", 
        dependencies=[Depends(only_staff)])
async def update_category(
    db: DBDep,
    data: CategoryUpdateDTO = Body(description="Данные о категории"),
    category_id: int = Path(),
):  
    try:
        await CategoryService(db).update_category(category_id=category_id, data=data)
    except CategoryNotFoundError as exc:
        raise CategoryNotFoundHTTPError from exc
    except CategoryExistsError as exc:
        raise CategoryExistsHTTPError from exc
    
    return {"status": "OK"}


@router.delete(
        path="/{category_id}", 
        summary="Удалить категорию шаблона | Только для персонала", 
        dependencies=[Depends(only_staff)])
async def delete_category(
    db: DBDep,
    category_id: int = Path(),
):
    try:
        await CategoryService(db).delete_category(category_id=category_id)
    except CategoryNotFoundError as exc:
        raise CategoryNotFoundHTTPError from exc
   
    return {"status": "OK"}
