from ferrox_py.core.provider import injectable
from typing import Any, Dict, Callable

@injectable()
class DistributedEventBus:
    def __init__(self):
        # Placeholder for Redis PubSub
        self._handlers: Dict[str, Callable] = {}

    def subscribe(self, event_name: str, handler: Callable):
        self._handlers[event_name] = handler

    async def publish(self, event_name: str, payload: Any):
        handler = self._handlers.get(event_name)
        if handler:
            await handler(payload)
