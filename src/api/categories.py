from pathlib import Path

from fastapi import APIRouter, Body, Depends
from fastapi_cache.decorator import cache

from src.dependencies.db import DBDep
from src.dependencies.users import only_staff
from src.schemas.categories import AddCategoryDTO, CategoryDTO, UpdateCategoryDTO
from src.services.categories import CategoryService
from src.api.examples.categories import EXAMPLE_CATEGORIES
from src.utils.exceptions import (
    CategoryExistsError,
    CategoryExistsHTTPError,
    CategoryInUseError,
    CategoryInUseHTTPError,
    CategoryNotFoundError,
    CategoryNotFoundHTTPError,
    ValueOutOfRangeError,
    ValueOutOfRangeHTTPError,
)


router = APIRouter(prefix="/categories", tags=["Категории шаблонов уведомлений"])


@router.get("", summary="Получить список всех категорий для шаблонов")
@cache(expire=120)
async def get_categories_list(
    db: DBDep,
):
    categories: list[CategoryDTO] = await CategoryService(db).get_categories_list()
    return {"status": "OK", "data": categories}


@router.get("/{category_id}", summary="Получить конкретную категорию по ID")
async def get_category(
    db: DBDep,
    category_id: int = Path(description="ID категории"),  # type: ignore
):
    try:
        category = await CategoryService(db).get_category(category_id=category_id)
    except CategoryNotFoundError as exc:
        raise CategoryNotFoundHTTPError from exc
    except ValueOutOfRangeError as exc:
        raise ValueOutOfRangeHTTPError(detail=exc.detail) from exc

    return {"status": "OK", "data": category}


@router.post(
    path="",
    summary="Добавить новую категорию | Только для персонала",
    dependencies=[Depends(only_staff)],
)
async def add_category(
    db: DBDep,
    data: AddCategoryDTO = Body(
        description="Данные о категории", openapi_examples=EXAMPLE_CATEGORIES
    ),
):
    try:
        category = await CategoryService(db).add_category(data=data)
    except CategoryNotFoundError as exc:
        raise CategoryNotFoundHTTPError from exc
    except CategoryExistsError as exc:
        raise CategoryExistsHTTPError from exc

    return {"data": category}


@router.patch(
    path="/{category_id}",
    summary="Обновить категорию шаблона | Только для персонала",
    dependencies=[Depends(only_staff)],
)
async def update_category(
    db: DBDep,
    data: UpdateCategoryDTO = Body(
        description="Данные о категории", openapi_examples=EXAMPLE_CATEGORIES
    ),
    category_id: int = Path("ID категории"),  # type: ignore
):
    try:
        await CategoryService(db).update_category(category_id=category_id, data=data)
    except CategoryNotFoundError as exc:
        raise CategoryNotFoundHTTPError from exc
    except CategoryExistsError as exc:
        raise CategoryExistsHTTPError from exc
    except ValueOutOfRangeError as exc:
        raise ValueOutOfRangeHTTPError(detail=exc.detail) from exc

    return {"status": "OK"}


@router.delete(
    path="/{category_id}",
    summary="Удалить категорию шаблона | Только для персонала",
    dependencies=[Depends(only_staff)],
)
async def delete_category(
    db: DBDep,
    category_id: int = Path("ID категории"),  # type: ignore
):
    try:
        await CategoryService(db).delete_category(category_id=category_id)
    except CategoryNotFoundError as exc:
        raise CategoryNotFoundHTTPError from exc
    except CategoryInUseError as exc:
        raise CategoryInUseHTTPError(detail=exc.detail) from exc
    except ValueOutOfRangeError as exc:
        raise ValueOutOfRangeHTTPError(detail=exc.detail) from exc

    return {"status": "OK"}
