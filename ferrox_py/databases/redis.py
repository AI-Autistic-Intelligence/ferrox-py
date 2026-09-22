import redis.asyncio as redis
from ferrox_py.core.provider import injectable

@injectable()
class RedisCacheService:
    def __init__(self, url: str = "redis://localhost:6379"):
        self.url = url
        self.client = None

    async def connect(self):
        self.client = redis.from_url(self.url, decode_responses=True)

    async def get(self, key: str) -> str:
        if self.client:
            return await self.client.get(key)
        return None

    async def set(self, key: str, value: str, ex: int = None):
        if self.client:
            await self.client.set(key, value, ex=ex)

    async def disconnect(self):
        if self.client:
            await self.client.aclose()
