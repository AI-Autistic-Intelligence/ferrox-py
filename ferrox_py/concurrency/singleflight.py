import asyncio
from collections.abc import Callable, Coroutine
from functools import wraps
from typing import Any, TypeVar, cast

T = TypeVar("T")

class SingleflightManager:
    def __init__(self) -> None:
        self._inflight: dict[str, asyncio.Future[Any]] = {}
        self._lock = asyncio.Lock()

    async def do(self, key: str, fn: Callable[[], Coroutine[Any, Any, T]]) -> T:
        wait_future = None
        async with self._lock:
            if key in self._inflight:
                wait_future = self._inflight[key]
            else:
                future = asyncio.get_running_loop().create_future()
                self._inflight[key] = future

        if wait_future is not None:
            return cast(T, await wait_future)

        try:
            result = await fn()
            future.set_result(result)
            return result
        except Exception as e:
            future.set_exception(e)
            _ = future.exception()  # Mark retrieved to avoid asyncio unhandled exception warning
            raise
        finally:
            async with self._lock:
                self._inflight.pop(key, None)

def singleflight(key_fn: Callable[..., str]) -> Callable[..., Any]:
    def decorator(func: Callable[..., Coroutine[Any, Any, T]]) -> Callable[..., Coroutine[Any, Any, T]]:
        manager = SingleflightManager()
        
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> T:
            key = key_fn(*args, **kwargs)
            async def call_fn() -> T:
                return await func(*args, **kwargs)
            return await manager.do(key, call_fn)
        
        return wrapper
    return decorator
