import asyncio
import time
from typing import Any

from redis.asyncio import Redis

from ferrox_py.core.provider import injectable

@injectable()
class RateLimiter:
    def __init__(self) -> None:
        # In-memory token bucket storage (for distributed, use DistributedRateLimiter)
        self._buckets: dict[str, Any] = {}
        self._lock = asyncio.Lock()

    async def is_allowed(self, key: str, capacity: int = 10, refill_rate: float = 1.0) -> bool:
        """
        Token bucket algorithm implementation.
        - capacity: max tokens in bucket
        - refill_rate: tokens added per second
        """
        now = time.time()
        async with self._lock:
            if key not in self._buckets:
                self._buckets[key] = {"tokens": float(capacity), "last_refill": now}

            bucket = self._buckets[key]
            time_passed = now - bucket["last_refill"]
            refill = time_passed * refill_rate

            if refill > 0:
                bucket["tokens"] = min(float(capacity), bucket["tokens"] + refill)
                bucket["last_refill"] = now

            if bucket["tokens"] >= 1:
                bucket["tokens"] -= 1
                return True
            return False

RATE_LIMIT_SCRIPT = """
local daily_key = KEYS[1]
local daily_limit = tonumber(ARGV[1])
local priority = ARGV[2]

local daily_count = tonumber(redis.call("get", daily_key) or "0")

-- Quota reservation: if priority is bulk and quota is below 20%, reject
if priority == "bulk" and daily_count >= (daily_limit * 0.8) then
    return 0
end

if daily_count >= daily_limit then
    return 0
end

redis.call("incr", daily_key)
if daily_count == 0 then
    -- Expire slightly after 24h to be safe
    redis.call("expire", daily_key, 86400 * 2) 
end

return 1
"""

@injectable()
class DistributedRateLimiter:
    def __init__(self, redis_client: Redis) -> None:
        self.redis = redis_client

    async def check_and_consume(self, key: str, max_concurrency: int = 1, daily_limit: int = 30000, priority: str = "interactive") -> bool:
        """
        Check and consume daily quota. Concurrency should be handled via locks or decorators.
        Returns True if allowed, False if limit exceeded or reserved.
        """
        today = time.strftime("%Y-%m-%d")
        daily_key = f"rate:{key}:daily:{today}"
        
        result = await self.redis.eval(RATE_LIMIT_SCRIPT, 1, daily_key, daily_limit, priority)
        return bool(result)
