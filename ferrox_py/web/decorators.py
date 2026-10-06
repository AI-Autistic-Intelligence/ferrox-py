from collections.abc import Callable
from typing import Any


def controller(prefix: str) -> Any:
    def decorator(cls) -> Any:  # type: ignore
        cls.__ferrox_prefix__ = prefix
        return cls
    return decorator

def get(path: str) -> Any:
    def decorator(func: Callable[..., Any]) -> Any:
        func.__ferrox_method__ = "GET"  # type: ignore
        func.__ferrox_path__ = path  # type: ignore
        return func
    return decorator

def post(path: str) -> Any:
    def decorator(func: Callable[..., Any]) -> Any:
        func.__ferrox_method__ = "POST"  # type: ignore
        func.__ferrox_path__ = path  # type: ignore
        return func
    return decorator

def use_guard(guard: Any) -> Any:
    def decorator(func: Callable[..., Any]) -> Any:
        if not hasattr(func, "__ferrox_guards__"):
            func.__ferrox_guards__ = []  # type: ignore
        func.__ferrox_guards__.append(guard)  # type: ignore
        return func
    return decorator
