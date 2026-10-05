from typing import Any, Callable, Dict, List, Optional, Type, Set, cast, AsyncGenerator, Any, Callable, Dict, List, Optional, Type, Set, cast, AsyncGenerator
import redis.asyncio as redis
from ferrox_py.core.provider import injectable

@injectable()
class RedisCacheService:
    def __init__(self, url: str = "redis://localhost:6379") -> None:
        self.url = url
        self.client: Optional[Any] = None

    async def connect(self) -> Any:
        self.client = redis.from_url(self.url, decode_responses=True)

    async def get(self, key: str) -> Optional[str]:
        if self.client:
            return cast(Optional[str], await self.client.get(key))
        return None

    async def set(self, key: str, value: str, ex: Optional[Optional[int]] = None) -> Any:
        if self.client:
            await self.client.set(key, value, ex=ex)

    async def disconnect(self) -> Any:
        if self.client:
            await self.client.aclose()
