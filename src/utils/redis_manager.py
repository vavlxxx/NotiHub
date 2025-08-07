from redis import Redis
from src.settings import settings


class RedisManager:
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port

    async def connect(self) -> Redis:
        self._redis = Redis(host=self.host, port=self.port)
        self._redis.ping()

    async def set(self, key: str, value: str, ex: int | None = None):
        await self._redis.set(name=key, value=value, ex=ex)

    async def get(self, key: str):
        return await self._redis.get(name=key)
    
    async def close(self):
        if self._redis:
            await self._redis.close()


redis_manager = RedisManager(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT
)
