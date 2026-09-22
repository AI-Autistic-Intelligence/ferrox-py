import inspect
from typing import Any, Callable, TypeVar, Type, Dict, Set

T = TypeVar("T")

class ProviderScope:
    SINGLETON = "singleton"
    TRANSIENT = "transient"
    SCOPED = "scoped"

def injectable(scope: str = ProviderScope.SINGLETON):
    """Decorator to mark a class as injectable."""
    def decorator(cls: Type[T]) -> Type[T]:
        if not inspect.isclass(cls):
            raise TypeError("@injectable can only be used on classes")
        cls.__ferrox_injectable__ = True
        cls.__ferrox_scope__ = scope
        return cls
    return decorator
