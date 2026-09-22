from typing import Callable, Any

def controller(prefix: str):
    def decorator(cls):
        cls.__ferrox_prefix__ = prefix
        return cls
    return decorator

def get(path: str):
    def decorator(func: Callable):
        func.__ferrox_method__ = "GET"
        func.__ferrox_path__ = path
        return func
    return decorator

def post(path: str):
    def decorator(func: Callable):
        func.__ferrox_method__ = "POST"
        func.__ferrox_path__ = path
        return func
    return decorator

def use_guard(guard: Any):
    def decorator(func: Callable):
        if not hasattr(func, "__ferrox_guards__"):
            func.__ferrox_guards__ = []
        func.__ferrox_guards__.append(guard)
        return func
    return decorator
