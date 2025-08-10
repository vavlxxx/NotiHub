import os

from typing_extensions import Self
from dataclasses import dataclass

import jinja2
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())


@dataclass(frozen=True, repr=False, eq=False, slots=True)
class Settings:

    DB_USER: str
    DB_PASS: str
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str

    DB_ADMIN_LOGIN: str
    DB_ADMIN_PASSWORD: str

    REDIS_HOST: str
    REDIS_PORT: int

    UVICORN_HOST: str
    UVICORN_PORT: int

    JWT_ALGORITHM: str
    JWT_SECRET_KEY: str
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int

    JINGA2_ENV: jinja2.Environment = jinja2.Environment(undefined=jinja2.StrictUndefined)

    def _get_env_var(env_var: str, to_cast: type) -> str:
        value = os.getenv(env_var)
        if value is None:
            raise ValueError(f'Env variable {env_var} is not set')
        return to_cast(value)

    @classmethod
    def load_from_env(cls) -> Self:
        return cls(
            DB_USER=cls._get_env_var('DB_USER', to_cast=str),
            DB_PASS=cls._get_env_var('DB_PASS', to_cast=str),
            DB_HOST=cls._get_env_var('DB_HOST', to_cast=str),
            DB_PORT=cls._get_env_var('DB_PORT', to_cast=int),
            DB_NAME=cls._get_env_var('DB_NAME', to_cast=str),

            DB_ADMIN_LOGIN=cls._get_env_var('DB_ADMIN_LOGIN', to_cast=str),
            DB_ADMIN_PASSWORD=cls._get_env_var('DB_ADMIN_PASSWORD', to_cast=str),

            REDIS_HOST=cls._get_env_var('REDIS_HOST', to_cast=str),
            REDIS_PORT=cls._get_env_var('REDIS_PORT', to_cast=int),

            UVICORN_HOST=cls._get_env_var('UVICORN_HOST', to_cast=str),
            UVICORN_PORT=cls._get_env_var('UVICORN_PORT', to_cast=int),

            JWT_ALGORITHM=cls._get_env_var('JWT_ALGORITHM', to_cast=str),
            JWT_SECRET_KEY=cls._get_env_var('JWT_SECRET_KEY', to_cast=str),
            JWT_ACCESS_TOKEN_EXPIRE_MINUTES=cls._get_env_var('JWT_ACCESS_TOKEN_EXPIRE_MINUTES', to_cast=int),
        )
    
    @property
    def redis_url(self):
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}"

    @property
    def database_url(self) -> str:
        return (f'postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}'
                f'@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}')


settings = Settings.load_from_env()
