import os
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

import json
import logging.config
from contextlib import asynccontextmanager

import uvicorn
from aiogram.types import Update
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend

from src.utils.db_manager import DB_Manager
from src.utils.redis_manager import redis_manager
from src.utils.enums import UserRole
from src.utils.exceptions import UserExistsError
from src.db import sessionmaker
from src.settings import settings
from src.schemas.users import RequestRegisterUserDTO
from src.services.users import UserService
from src.bot.bot import bot, dp

from src.api.templates import router as router_templates
from src.api.categories import router as router_categories
from src.api.docs import router as router_docs
from src.api.users import router as router_users
from src.api.channels import router as router_channels
from src.api.notifications import router as router_notifications


def configurate_logging(root_logger_name: str):
    basepath = Path(__file__).resolve().parent.parent
    with open(basepath / "logging_config.json", "r") as f:
        config = json.load(f)

    os.makedirs(basepath / "logs", exist_ok=True)
    logging.config.dictConfig(config)
    return logging.getLogger(root_logger_name)


logger = configurate_logging("src")


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with DB_Manager(sessionmaker) as db:
        await db.check_connection()
        logger.info("Successfully connected to DB")

        try:
            await UserService(db).add_user(
                RequestRegisterUserDTO(
                    username=settings.DB_ADMIN_LOGIN,
                    password=settings.DB_ADMIN_PASSWORD,
                    role=UserRole.ADMIN,
                )
            )
            logger.info("Added admin user")
        except UserExistsError:
            logger.info("Admin user already exists, skipping...")

    await redis_manager.connect()
    logger.info("Successfully connected to Redis")

    FastAPICache.init(RedisBackend(redis_manager._redis), prefix="fastapi-cache")
    logger.info("FastAPICache initialized...")

    await bot.set_webhook(
        url=settings.TELEGRAM_WEBHOOK_URL,
        allowed_updates=dp.resolve_used_update_types(),
        drop_pending_updates=True,
    )
    await bot.send_message(
        chat_id=settings.TELEGRAM_ADMIN_CONTACT, text="🚀 Bot has been started..."
    )
    logger.info("Aiogram webhook has been set...")

    yield

    await bot.send_message(
        chat_id=settings.TELEGRAM_ADMIN_CONTACT, text="🛑 Bot has been stopped..."
    )
    await bot.delete_webhook(drop_pending_updates=True)
    logger.info("Aiogram webhook has been deleted...")
    await bot.session.close()

    await redis_manager.close()
    logger.info("Connection to Redis has been closed")


app = FastAPI(title=settings.APP_NAME, lifespan=lifespan, docs_url=None, redoc_url=None)
app.include_router(router=router_docs)
app.include_router(router=router_templates)
app.include_router(router=router_categories)
app.include_router(router=router_users)
app.include_router(router=router_channels)
app.include_router(router=router_notifications)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/webhook", include_in_schema=False)
async def webhook_handler(request: Request):
    webhook_data = await request.json()
    update = Update(**webhook_data)
    await dp.feed_update(bot, update)
    return {"status": "OK"}


if __name__ == "__main__":
    uvicorn.run(
        "main:app", reload=True, host=settings.UVICORN_HOST, port=settings.UVICORN_PORT
    )
