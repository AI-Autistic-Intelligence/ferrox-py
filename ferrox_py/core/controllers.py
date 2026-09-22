from fastapi import APIRouter
from typing import Any

class BaseController:
    """
    Base class for controllers in the framework.
    Standardizes response formatting and provides an APIRouter.
    """
    def __init__(self, prefix: str = "", tags: list = None):
        self.router = APIRouter(prefix=prefix, tags=tags or [])

    def ok(self, data: Any = None, message: str = "Success"):
        return {"status": "ok", "message": message, "data": data}
        
    def created(self, data: Any = None, message: str = "Created"):
        return {"status": "created", "message": message, "data": data}
