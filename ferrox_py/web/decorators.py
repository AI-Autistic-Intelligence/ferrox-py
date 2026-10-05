from typing import Any, Callable, Dict, List, Optional, Type, Set, cast, AsyncGenerator, Callable, Any

def controller(prefix: str) -> Any:
    def decorator(cls) -> Any:
        cls.__ferrox_prefix__ = prefix
        return cls
    return decorator

def get(path: str) -> Any:
    def decorator(func: Callable[..., Any]) -> Any:
        setattr(func, '__ferrox_method__', "GET")
        setattr(func, '__ferrox_path__', path)
        return func
    return decorator

def post(path: str) -> Any:
    def decorator(func: Callable[..., Any]) -> Any:
        setattr(func, '__ferrox_method__', "POST")
        setattr(func, '__ferrox_path__', path)
        return func
    return decorator

def use_guard(guard: Any) -> Any:
    def decorator(func: Callable[..., Any]) -> Any:
        if not hasattr(func, "__ferrox_guards__"):
            setattr(func, '__ferrox_guards__', [])
        func.__ferrox_guards__.append(guard)
        return func
    return decorator
