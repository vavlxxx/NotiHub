from sqlalchemy import NullPool
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from src.settings import settings


engine = create_async_engine(url=settings.database_url, echo=False)
sessionmaker = async_sessionmaker(bind=engine, expire_on_commit=False)

engine_null_pool = create_async_engine(url=settings.database_url, poolclass=NullPool)
sessionmaker_null_pool = async_sessionmaker(bind=engine_null_pool, expire_on_commit=False)
