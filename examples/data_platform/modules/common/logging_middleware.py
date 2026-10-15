import json
import logging
import time
import uuid
from datetime import datetime, timezone
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger("ferrox.data_platform")
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)


class StructuredJsonLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        start_time = time.perf_counter()

        # Extract or generate correlation ID
        correlation_id = request.headers.get("x-correlation-id") or str(uuid.uuid4())
        
        # Extract or generate trace ID (supporting W3C traceparent)
        trace_id = request.headers.get("x-trace-id")
        if not trace_id:
            traceparent = request.headers.get("traceparent")
            if traceparent and len(traceparent.split("-")) >= 3:
                trace_id = traceparent.split("-")[1]
            else:
                trace_id = uuid.uuid4().hex

        # Inject into request state for downstream handlers
        request.state.correlation_id = correlation_id
        request.state.trace_id = trace_id

        client_ip = request.client.host if request.client else "unknown"

        try:
            response = await call_next(request)
            status_code = response.status_code
        except Exception as exc:
            duration_ms = round((time.perf_counter() - start_time) * 1000, 2)
            log_record = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "level": "ERROR",
                "correlation_id": correlation_id,
                "trace_id": trace_id,
                "method": request.method,
                "path": request.url.path,
                "status_code": 500,
                "duration_ms": duration_ms,
                "client_ip": client_ip,
                "error": str(exc),
            }
            logger.error(json.dumps(log_record))
            raise exc

        duration_ms = round((time.perf_counter() - start_time) * 1000, 2)

        # Build structured JSON log record
        log_record = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": "INFO" if status_code < 400 else ("WARN" if status_code < 500 else "ERROR"),
            "correlation_id": correlation_id,
            "trace_id": trace_id,
            "method": request.method,
            "path": request.url.path,
            "status_code": status_code,
            "duration_ms": duration_ms,
            "client_ip": client_ip,
        }
        logger.info(json.dumps(log_record))

        # Attach telemetry headers to response
        response.headers["x-correlation-id"] = correlation_id
        response.headers["x-trace-id"] = trace_id
        response.headers["x-response-time-ms"] = str(duration_ms)

        return response
