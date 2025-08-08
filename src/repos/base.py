from typing import Any, Sequence

from asyncpg import UniqueViolationError, DataError
from sqlalchemy import delete, select, insert, update
from sqlalchemy.exc import NoResultFound, IntegrityError, DBAPIError
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.base import Base
from src.schemas.base import BaseDTO
from src.utils.exceptions import ObjectNotFoundError, ObjectExistsError, InvalidDBDataError


class BaseRepository:
    model: type[Base]
    schema: type[BaseDTO]
    session: AsyncSession


    def __init__(self, session: AsyncSession):
        self.session = session


    async def get_all_filtered(self, *filter, **filter_by) -> list[BaseDTO | Any]:
        query = select(self.model).filter(*filter).filter_by(**filter_by)
        result = await self.session.execute(query)
        return [self.schema.model_validate(obj) for obj in result.scalars().all()]


    async def get_all(self) -> list[BaseDTO]:
        return await self.get_all_filtered()


    async def get_one_or_none(self, *filter, **filter_by) -> BaseDTO | None | Any:
        query = select(self.model).filter(*filter).filter_by(**filter_by)
        result = await self.session.execute(query)
        obj = result.scalars().one_or_none()
        if obj is None:
            return None
        return self.schema.model_validate(obj)


    async def get_one(self, *filter, **filter_by) -> BaseDTO | Any:
        query = select(self.model).filter(*filter).filter_by(**filter_by)
        try:
            result = await self.session.execute(query)
            obj = result.scalar_one()
        except NoResultFound:
            raise ObjectNotFoundError
        except DBAPIError as exc:
            if isinstance(exc.orig.__cause__, DataError):  # type: ignore
                raise InvalidDBDataError from exc
            raise exc

        return self.schema.model_validate(obj)


    async def add_bulk(self, data: Sequence[BaseDTO]):
        add_obj_stmt = insert(self.model).values([item.model_dump() for item in data])
        await self.session.execute(add_obj_stmt)


    async def add(self, data: BaseDTO, **params):
        add_obj_stmt = (
            insert(self.model).values(**data.model_dump(), **params).returning(self.model)
        )
        try:
            result = await self.session.execute(add_obj_stmt)
        except IntegrityError as exc:
            if isinstance(exc.orig.__cause__, UniqueViolationError):  # type: ignore
                raise ObjectExistsError from exc
            raise exc

        obj = result.scalars().one()
        return self.schema.model_validate(obj)


    async def get_one_or_add(self, data: BaseDTO, **params):
        obj = await self.get_one_or_none(**data.model_dump())
        if obj is None:
            return await self.add(data, **params)
        return self.schema.model_validate(obj)


    async def edit(self, data: BaseDTO, exclude_unset=True, exclude_fields=None, *filter, **filter_by):
        await self.get_one(*filter, **filter_by)
        exclude_fields = exclude_fields or set()
        to_update = data.model_dump(exclude=exclude_fields, exclude_unset=exclude_unset)
        if not to_update:
            return
        edit_obj_stmt = update(self.model).filter_by(**filter_by).values(**to_update)

        try:
            await self.session.execute(edit_obj_stmt)
        except IntegrityError as exc:
            if isinstance(exc.orig.__cause__, UniqueViolationError):  # type: ignore
                raise ObjectExistsError from exc
            raise exc


    async def delete(self, *filter, **filter_by):
        await self.get_one(*filter, **filter_by)
        delete_obj_stmt = delete(self.model).filter(*filter).filter_by(**filter_by)
        await self.session.execute(delete_obj_stmt)
