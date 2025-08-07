import sys
import asyncio
from pathlib import Path

from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

sys.path.append(str(Path(__file__).resolve().parent.parent))

from src.db import sessionmaker
from src.utils.db_manager import DB_Manager
from src.schemas.templates import TemplateAddDTO
from src.services.templates import TemplateService


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with DB_Manager(sessionmaker) as db:
        await db.check_connection()
    yield


app = FastAPI(title="NotiHub", lifespan=lifespan)


async def main():
    obj = TemplateAddDTO(title="Заказ {{ order_number }} подтвержден", content="Здравствуйте, {{ name }}! Ваш заказ на сумму {{ amount }} принят в обработку")
    async with DB_Manager(sessionmaker) as db:
        print(await TemplateService(db).add_template(obj))




if __name__ == "__main__":
    asyncio.run(main())
    # uvicorn.run("main:app", host="0.0.0.0", port=8888)