from typing import Any, Callable, Dict, List, Optional, Type, Set, cast, AsyncGenerator, Callable
import asyncio

def cron(expression: str) -> Any:
    """
    Decorator to schedule a task via cron expression.
    Requires APScheduler integration to be active in the container.
    """
    def decorator(func: Callable[..., Any]) -> Any:
        func.__ferrox_cron__ = expression  # type: ignore
        return func
    return decorator

def interval(seconds: int) -> Any:
    """
    Decorator to run a task repeatedly.
    """
    def decorator(func: Callable[..., Any]) -> Any:
        func.__ferrox_interval__ = seconds  # type: ignore
        return func
    return decorator
