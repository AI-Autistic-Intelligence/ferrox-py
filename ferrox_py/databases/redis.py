from typing import Any, cast

import redis.asyncio as redis

from ferrox_py.core.provider import injectable


@injectable()
class RedisCacheService:
    def __init__(self, url: str = "redis://localhost:6379") -> None:
        self.url = url
        self.client: Any | None = None

    async def connect(self) -> Any:
        self.client = redis.from_url(self.url, decode_responses=True)

    async def get(self, key: str) -> str | None:
        if self.client:
            return cast(str | None, await self.client.get(key))
        return None

    async def set(self, key: str, value: str, ex: int | None = None) -> Any:
        if self.client:
            await self.client.set(key, value, ex=ex)

    async def disconnect(self) -> Any:
        if self.client:
            await self.client.aclose()

@injectable()
class FerroxRedis(redis.Redis):
    """
    Subclass of redis.asyncio.Redis that is registered in the IoC container.
    Services like DistributedLockManager can depend on FerroxRedis.
    """
