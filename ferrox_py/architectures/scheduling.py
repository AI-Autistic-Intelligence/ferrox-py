from typing import Callable
import asyncio

def cron(expression: str):
    """
    Decorator to schedule a task via cron expression.
    Requires APScheduler integration to be active in the container.
    """
    def decorator(func: Callable):
        func.__ferrox_cron__ = expression
        return func
    return decorator

def interval(seconds: int):
    """
    Decorator to run a task repeatedly.
    """
    def decorator(func: Callable):
        func.__ferrox_interval__ = seconds
        return func
    return decorator
