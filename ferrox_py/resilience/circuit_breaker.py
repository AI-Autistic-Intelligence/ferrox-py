import asyncio
import time
from collections.abc import Callable
from typing import Any

from redis.asyncio import Redis

from ferrox_py.core.utils import to_str


class CircuitBreakerOpenException(Exception):
    pass

class CircuitBreaker:
    def __init__(self, max_failures: int = 5, reset_timeout: int = 60) -> None:
        self.max_failures = max_failures
        self.reset_timeout = reset_timeout
        self.failures = 0
        self.last_failure_time = 0.0
        self.state = "CLOSED"

    async def call(self, func: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
        if self.state == "OPEN":
            if time.time() - self.last_failure_time > self.reset_timeout:
                self.state = "HALF_OPEN"
            else:
                raise CircuitBreakerOpenException("Circuit breaker is OPEN")

        try:
            if asyncio.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)
                
            self.failures = 0
            self.state = "CLOSED"
            return result
        except Exception as e:
            self.failures += 1
            self.last_failure_time = time.time()
            if self.failures >= self.max_failures:
                self.state = "OPEN"
            raise e

class FailureBudgetGuard:
    def __init__(self, redis_client: Redis, max_failures: int = 200, window_seconds: int = 86400) -> None:
        self.redis = redis_client
        self.max_failures = max_failures
        self.window_seconds = window_seconds

    async def is_open(self, tenant_id: str, provider: str) -> bool:
        key = f"cb:budget:{tenant_id}:{provider}"
        failures = await self.redis.get(key)
        return int(failures or 0) >= self.max_failures

    async def record_failure(self, tenant_id: str, provider: str) -> None:
        key = f"cb:budget:{tenant_id}:{provider}"
        pipe = self.redis.pipeline()
        pipe.incr(key)
        # expire nx essentially available in Redis 7, but for backwards compatibility:
        # we can just use a lua script or simpler:
        ttl = await self.redis.ttl(key)
        if ttl == -1:
            pipe.expire(key, self.window_seconds)
        await pipe.execute()

class DistributedCircuitBreaker:
    def __init__(self, redis_client: Redis, max_failures: int = 5, reset_timeout: int = 60, budget_failures: int = 200) -> None:
        self.redis = redis_client
        self.max_failures = max_failures
        self.reset_timeout = reset_timeout
        self.guard = FailureBudgetGuard(redis_client, max_failures=budget_failures)

    async def call(self, tenant_id: str, provider: str, func: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
        if await self.guard.is_open(tenant_id, provider):
            raise CircuitBreakerOpenException(f"Failure budget exceeded for {provider}")

        cb_key = f"cb:state:{tenant_id}:{provider}"
        failures_key = f"cb:failures:{tenant_id}:{provider}"
        
        state_bytes = await self.redis.get(cb_key)
        state = to_str(state_bytes) if state_bytes else "CLOSED"

        if state == "OPEN":
            raise CircuitBreakerOpenException(f"Circuit breaker is OPEN for {provider}")

        try:
            if asyncio.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)
                
            if state == "HALF_OPEN":
                await self.redis.set(cb_key, "CLOSED")
                await self.redis.set(failures_key, "0")
            
            return result
        except Exception as e:
            # We record a failure
            failures = await self.redis.incr(failures_key)
            if failures == 1:
                await self.redis.expire(failures_key, self.reset_timeout * 2)
                
            if failures >= self.max_failures:
                # Setting to OPEN with EX means it goes missing (CLOSED) after reset_timeout.
                await self.redis.set(cb_key, "OPEN", ex=self.reset_timeout)
            
            # Also record in failure budget
            await self.guard.record_failure(tenant_id, provider)
            raise e
