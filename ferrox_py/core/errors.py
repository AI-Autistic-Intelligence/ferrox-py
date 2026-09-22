from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

class FerroxError(Exception):
    """Base exception for Ferrox errors."""
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code

def setup_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(FerroxError)
    async def ferrox_error_handler(request: Request, exc: FerroxError):
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": True, "message": exc.message}
        )
