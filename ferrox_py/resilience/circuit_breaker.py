import time
import asyncio
from typing import Any, Callable, Dict, List, Optional, Type, Set, cast, AsyncGenerator, Any, Callable, Dict, List, Optional, Type, Set, cast, AsyncGenerator, Callable, Any

class CircuitBreakerOpenException(Exception):
    pass

class CircuitBreaker:
    def __init__(self, max_failures: int = 5, reset_timeout: int = 60) -> None:
        self.max_failures = max_failures
        self.reset_timeout = reset_timeout
        self.failures = 0
        self.last_failure_time = 0.0
        self.state = "CLOSED"

    async def call(self, func: Callable[..., Any], *args, **kwargs) -> Any:
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
