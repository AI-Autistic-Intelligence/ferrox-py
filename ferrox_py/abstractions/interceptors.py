from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import Any


class Interceptor(ABC):
    @abstractmethod
    async def intercept(self, request: Any, next_handler: Callable[..., Any]) -> Any:
        """
        Intercept the execution of a route handler.
        `next_handler` must be awaited to proceed to the controller.
        """

class LoggingInterceptor(Interceptor):
    async def intercept(self, request: Any, next_handler: Callable[..., Any]) -> Any:
        # Example before execution
        print(f"Incoming request: {getattr(request, 'url', 'Unknown')}")
        
        # Execute handler
        response = await next_handler()
        
        # Example after execution
        print("Request completed.")
        return response
