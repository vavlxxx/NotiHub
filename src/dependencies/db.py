from typing import Annotated
from fastapi import Depends

from src.utils.db_manager import DB_Manager
from src.db import sessionmaker


async def get_db():
    async with DB_Manager(session_factory=sessionmaker) as db:
        yield db


DBDep = Annotated[DB_Manager, Depends(get_db)]
