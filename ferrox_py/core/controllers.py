from typing import Any

from fastapi import APIRouter


class BaseController:
    """
    Base class for controllers in the framework.
    Standardizes response formatting and provides an APIRouter.
    """
    def __init__(self, prefix: str = "", tags: list[Any] | None = None) -> None:
        self.router = APIRouter(prefix=prefix, tags=tags or [])

    def ok(self, data: Any | None = None, message: str = "Success") -> Any:
        return {"status": "ok", "message": message, "data": data}
        
    def created(self, data: Any | None = None, message: str = "Created") -> Any:
        return {"status": "created", "message": message, "data": data}
