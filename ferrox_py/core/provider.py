import inspect
from typing import (
    Any,
    TypeVar,
)

T = TypeVar("T")

class ProviderScope:
    SINGLETON = "singleton"
    TRANSIENT = "transient"
    SCOPED = "scoped"

def injectable(scope: str = ProviderScope.SINGLETON) -> Any:
    """Decorator to mark a class as injectable."""
    def decorator(cls: type[T]) -> type[T]:
        if not inspect.isclass(cls):
            raise TypeError("@injectable can only be used on classes")
        cls.__ferrox_injectable__ = True  # type: ignore
        cls.__ferrox_scope__ = scope  # type: ignore
        return cls
    return decorator
