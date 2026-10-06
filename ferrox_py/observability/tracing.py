import uuid
from contextvars import ContextVar
from typing import Any

from ferrox_py.core.provider import injectable

# Simple distributed tracing mock context
trace_id_ctx_var: ContextVar[str] = ContextVar("trace_id", default="")

@injectable()
class TracingService:
    def start_trace(self) -> str:
        trace_id = str(uuid.uuid4())
        trace_id_ctx_var.set(trace_id)
        return trace_id
        
    def get_current_trace_id(self) -> str:
        return trace_id_ctx_var.get()
        
    def log_span(self, name: str, duration_ms: float) -> Any:
        trace_id = self.get_current_trace_id()
        # In a real setup, this exports to OpenTelemetry collector (Jaeger/Zipkin)
        print(f"[TRACE {trace_id}] Span '{name}' took {duration_ms:.2f}ms")
