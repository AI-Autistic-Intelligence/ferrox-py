from fastapi import APIRouter
from typing import Any, Callable, Dict, List, Optional, Type, Set, cast, AsyncGenerator, Any, Callable, Dict, List, Optional, Type, Set, cast, AsyncGenerator, Any

class BaseController:
    """
    Base class for controllers in the framework.
    Standardizes response formatting and provides an APIRouter.
    """
    def __init__(self, prefix: str = "", tags: Optional[Optional[List[Any]]] = None) -> None:
        self.router = APIRouter(prefix=prefix, tags=tags or [])

    def ok(self, data: Optional[Optional[Any]] = None, message: str = "Success") -> Any:
        return {"status": "ok", "message": message, "data": data}
        
    def created(self, data: Optional[Optional[Any]] = None, message: str = "Created") -> Any:
        return {"status": "created", "message": message, "data": data}
