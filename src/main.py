import logging
import sys
from pathlib import Path
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

sys.path.append(str(Path(__file__).resolve().parent.parent))
from src.db import sessionmaker
from src.utils.db_manager import DB_Manager
from src.settings import settings
from src.utils.redis_manager import redis_manager
from src.api.templates import router as router_templates
from src.api.docs import router as router_docs


logging.basicConfig(
    level=logging.INFO,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with DB_Manager(sessionmaker) as db:
        await db.check_connection()

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


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        reload=True,
        host=settings.UVICORN_HOST, 
        port=settings.UVICORN_PORT
    )
