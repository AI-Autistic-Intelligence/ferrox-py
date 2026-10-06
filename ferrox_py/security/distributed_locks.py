import asyncio
import uuid
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from typing import Optional

from redis.asyncio import Redis

from ferrox_py.core.errors import FerroxError
from ferrox_py.core.provider import injectable

RELEASE_SCRIPT = """
if redis.call("get", KEYS[1]) == ARGV[1] then
    return redis.call("del", KEYS[1])
else
    return 0
end
"""

@injectable()
class DistributedLockManager:
    def __init__(self, redis_client: Redis | None = None) -> None:
        self.redis = redis_client
        self._in_memory_locks: dict[str, str] = {}
        self._mutex = asyncio.Lock()

    @asynccontextmanager
    async def acquire(self, key: str, ttl_ms: int = 10000, timeout_ms: int = 5000) -> AsyncGenerator[str, None]:
        """
        Acquires a distributed lock. If redis is available, uses Redis SET NX PX.
        Otherwise falls back to an in-memory lock table.
        If timeout is reached, raises FerroxError.
        """
        lock_id = str(uuid.uuid4())
        loop = asyncio.get_running_loop()
        start_time = loop.time()
        acquired = False

        if self.redis is not None:
            while (loop.time() - start_time) * 1000 < timeout_ms:
                if await self.redis.set(key, lock_id, nx=True, px=ttl_ms):
                    acquired = True
                    break
                await asyncio.sleep(0.05)  # Backoff

            if not acquired:
                raise FerroxError(message=f"Failed to acquire lock for key {key}", status_code=423)

            try:
                yield lock_id
            finally:
                await self.redis.eval(RELEASE_SCRIPT, 1, key, lock_id)
        else:
            while (loop.time() - start_time) * 1000 < timeout_ms:
                async with self._mutex:
                    if key not in self._in_memory_locks:
                        self._in_memory_locks[key] = lock_id
                        acquired = True
                        break
                await asyncio.sleep(0.05)

            if not acquired:
                raise FerroxError(message=f"Failed to acquire lock for key {key}", status_code=423)

            try:
                yield lock_id
            finally:
                async with self._mutex:
                    if self._in_memory_locks.get(key) == lock_id:
                        del self._in_memory_locks[key]
