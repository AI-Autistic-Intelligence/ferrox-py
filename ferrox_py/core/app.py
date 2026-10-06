from typing import Any

from fastapi import FastAPI

from ferrox_py.core.errors import setup_exception_handlers
from ferrox_py.security.headers import MandatorySecurityHeadersMiddleware


class FerroxApp:
    def __init__(self, title: str = "Ferrox-Py API", version: str = "0.1.0"):
        self._app = FastAPI(title=title, version=version)
        self._setup_pipeline()
    
    def _setup_pipeline(self) -> None:
        # Layer 1: Security Header Enforcer Middleware
        self._app.add_middleware(MandatorySecurityHeadersMiddleware)
        # Setup Global Exception Handlers
        setup_exception_handlers(self._app)

    @property
    def asgi_app(self) -> FastAPI:
        """Returns the underlying FastAPI application for ASGI servers."""
        return self._app

    def include_router(self, router: Any) -> None:
        """Includes a FastAPI router."""
        self._app.include_router(router)
