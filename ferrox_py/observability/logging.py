import structlog
import uuid
from contextvars import ContextVar

correlation_id: ContextVar[str] = ContextVar("correlation_id", default="")

def get_logger(name: str):
    structlog.configure(
        processors=[
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.JSONRenderer()
        ]
    )
    return structlog.get_logger(name)

def set_correlation_id(cid: str = None) -> str:
    if not cid:
        cid = str(uuid.uuid4())
    correlation_id.set(cid)
    return cid
