from typing import Any, Callable, Dict, List, Optional, Type, Set, cast, AsyncGenerator, Any, Callable, Dict, List, Optional, Type, Set, cast, AsyncGenerator
import asyncio
import uuid
from contextlib import asynccontextmanager
from ferrox_py.core.provider import injectable
from ferrox_py.core.errors import FerroxError

@injectable()
class DistributedLockManager:
    def __init__(self) -> None:
        # In-memory mock for Redlock algorithm
        self._locks: Dict[str, Any] = {}
        self._mutex = asyncio.Lock()

    @asynccontextmanager
    async def acquire(self, key: str, ttl_ms: int = 10000, timeout_ms: int = 5000) -> Any:
        """
        Acquires a distributed lock. If timeout is reached, raises FerroxError.
        """
        lock_id = str(uuid.uuid4())
        start_time = asyncio.get_event_loop().time()
        acquired = False
        
        while (asyncio.get_event_loop().time() - start_time) * 1000 < timeout_ms:
            async with self._mutex:
                if key not in self._locks:
                    self._locks[key] = lock_id
                    acquired = True
                    break
            await asyncio.sleep(0.05) # Backoff
            
        if not acquired:
            raise FerroxError(message=f"Failed to acquire lock for key {key}", status_code=423)
            
        try:
            # Yield control back to caller while holding lock
            yield lock_id
        finally:
            async with self._mutex:
                if self._locks.get(key) == lock_id:
                    del self._locks[key]
