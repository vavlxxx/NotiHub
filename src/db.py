from sqlalchemy import NullPool
from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker, create_async_engine

from src.settings import settings

engine: AsyncEngine = create_async_engine(
    url=settings.database_url,
    echo=False,
)
sessionmaker: async_sessionmaker = async_sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
)
engine_null_pool: AsyncEngine = create_async_engine(
    url=settings.database_url,
    poolclass=NullPool,
)
sessionmaker_null_pool: async_sessionmaker = async_sessionmaker(
    bind=engine_null_pool,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
)
