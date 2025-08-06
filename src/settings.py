import os
from typing_extensions import Self
from dataclasses import dataclass

from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())


@dataclass(frozen=True, repr=False, eq=False, slots=True)
class Settings:

    DB_USER: str
    DB_PASS: str
    DB_HOST: str
    DB_PORT: str
    DB_NAME: str

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
            DB_PORT=cls._get_env_var('DB_PORT', to_cast=str),
            DB_NAME=cls._get_env_var('DB_NAME', to_cast=str),
        )
    
    @property
    def database_url(self) -> str:
        return (f'postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}'
                f'@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}')


settings = Settings.load_from_env()
