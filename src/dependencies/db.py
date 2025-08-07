from typing import Annotated
from fastapi import Depends

from src.utils.db_manager import DB_Manager
from src.db import sessionmaker


def get_db_manager():
    return DB_Manager(session_factory=sessionmaker)


async def get_db():
    async with get_db_manager() as db:
        yield db
DBDep = Annotated[DB_Manager, Depends(get_db)]
