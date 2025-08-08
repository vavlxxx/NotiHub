import logging
import sys
from pathlib import Path
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

sys.path.append(str(Path(__file__).resolve().parent.parent))
from src.utils.db_manager import DB_Manager
from src.utils.redis_manager import redis_manager

from src.db import sessionmaker
from src.settings import settings
from src.schemas.users import UserRegisterRequestDTO
from src.services.users import UserService

from src.api.templates import router as router_templates
from src.api.docs import router as router_docs
from src.api.users import router as router_users

logging.basicConfig(
    level=logging.INFO,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with DB_Manager(sessionmaker) as db:
        await db.check_connection()

        await UserService(db).get_one_or_add(
            UserRegisterRequestDTO(
                username=settings.DB_ADMIN_LOGIN, 
                password=settings.DB_ADMIN_PASSWORD
            )
        )

    await redis_manager.connect()
    logging.info("Successfully connected to Redis")
    yield
    await redis_manager.close()
    logging.info("Redis connection closed")


app = FastAPI(
    title="NotiHub", 
    lifespan=lifespan,
    docs_url=None, 
    redoc_url=None
)
app.include_router(router=router_docs)
app.include_router(router=router_templates)
app.include_router(router=router_users)


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        reload=True,
        host=settings.UVICORN_HOST, 
        port=settings.UVICORN_PORT
    )
