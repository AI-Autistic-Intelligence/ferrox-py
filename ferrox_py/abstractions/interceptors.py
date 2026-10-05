from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, List, Optional, Type, Set, cast, AsyncGenerator, Any, Callable, Dict, List, Optional, Type, Set, cast, AsyncGenerator, Any, Callable

class Interceptor(ABC):
    @abstractmethod
    async def intercept(self, request: Any, next_handler: Callable[..., Any]) -> Any:
        """
        Intercept the execution of a route handler.
        `next_handler` must be awaited to proceed to the controller.
        """
        pass

class LoggingInterceptor(Interceptor):
    async def intercept(self, request: Any, next_handler: Callable[..., Any]) -> Any:
        # Example before execution
        print(f"Incoming request: {getattr(request, 'url', 'Unknown')}")
        
        # Execute handler
        response = await next_handler()
        
        # Example after execution
        print(f"Request completed.")
        return response
