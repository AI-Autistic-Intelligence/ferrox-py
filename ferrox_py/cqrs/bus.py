from collections.abc import Callable
from typing import Any, TypeVar

T = TypeVar("T")
R = TypeVar("R")

class CQRSBus:
    def __init__(self) -> None:
        self._handlers: dict[str, Callable[..., Any]] = {}

    def register(self, name: str, handler: Callable[..., Any]) -> Any:
        self._handlers[name] = handler

    async def execute(self, name: str, payload: Any) -> Any:
        handler = self._handlers.get(name)
        if not handler:
            raise ValueError(f"No handler registered for {name}")
        return await handler(payload)

class CommandBus(CQRSBus):
    pass

class QueryBus(CQRSBus):
    pass

class EventBus(CQRSBus):
    async def publish(self, name: str, payload: Any) -> None:
        handler = self._handlers.get(name)
        if handler:
            await handler(payload)
