from typing import Any, Callable, Dict, List, Optional, Type, Set, cast, AsyncGenerator, Any, Callable, Dict, List, Optional, Type, Set, cast, AsyncGenerator
import time
import asyncio
from ferrox_py.core.provider import injectable

@injectable()
class RateLimiter:
    def __init__(self) -> None:
        # In-memory token bucket storage (for distributed, use Redis)
        self._buckets: Dict[str, Any] = {}
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
                self._buckets[key] = {"tokens": capacity, "last_refill": now}
            
            bucket = self._buckets[key]
            
            # Refill logic
            time_passed = now - bucket["last_refill"]
            refill = time_passed * refill_rate
            
            if refill > 0:
                bucket["tokens"] = min(capacity, bucket["tokens"] + refill)
                bucket["last_refill"] = now
            
            # Consume logic
            if bucket["tokens"] >= 1:
                bucket["tokens"] -= 1
                return True
            return False
