from collections.abc import Callable
from typing import Any

from ferrox_py.core.provider import injectable


@injectable()
class DistributedEventBus:
    def __init__(self) -> None:
        # Placeholder for Redis PubSub
        self._handlers: dict[str, Callable[..., Any]] = {}

    def subscribe(self, event_name: str, handler: Callable[..., Any]) -> Any:
        self._handlers[event_name] = handler

    async def publish(self, event_name: str, payload: Any) -> Any:
        handler = self._handlers.get(event_name)
        if handler:
            await handler(payload)
