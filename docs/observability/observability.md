# Observability Component

## 1. Overview (What does this do?)
The Observability component provides built-in mechanisms for logging, tracing, and monitoring the health of a `ferrox-py` application. It centralizes output streams, ensuring that all log messages generated within a single request lifecycle are tied together via a unique Correlation ID.

## 2. Philosophy (Why does it exist?)
In asynchronous Python applications, traditional logging mechanisms often fail to track a single request accurately because multiple concurrent requests interleave their logs. The philosophy here is that developers shouldn't have to manually pass a logger object to every function. By leveraging `ContextVars`, the framework ensures that logs are asynchronous-safe and natively structured.

## 3. Target Audience (Who is it for?)
This component is vital for DevOps engineers, Site Reliability Engineers (SREs), and backend developers who need to debug complex asynchronous flows in production using modern log aggregators like Datadog, ELK, or Grafana Loki.

## 4. Architecture (How does it work?)
- **Structured Logging (Structlog)**: Instead of plain text strings, logs are emitted as structured JSON objects, making them infinitely easier to index and search.
- **Correlation IDs**: At Layer 1 (Security Header Enforcer Middleware), a unique `X-Request-ID` is either parsed from the incoming request or generated. This ID is injected into a ContextVar. Every subsequent log emitted during that request's lifecycle automatically includes this Correlation ID.
- **Metrics**: The observability module hooks into the application lifecycle to expose standard Prometheus-compatible metrics (like HTTP response times and error rates) if configured.

## 5. Installation / Setup
The core logging functionality is built-in, but it heavily leverages the `structlog` library.

```bash
pip install structlog
```
Configuration is automatically handled during the `FerroxApp` initialization, but can be customized by passing a configuration dictionary to the IoC Container.

## 6. Quickstart (Usage)
```python
from ferrox_py.core.observability import get_logger

# The logger is a singleton configured by the container, 
# but it automatically pulls context from the current asyncio task.
logger = get_logger("my_domain_service")

async def process_payment(amount: float):
    # This log will automatically include the 'request_id' 
    # without you passing it manually!
    logger.info("Processing payment", amount=amount, currency="USD")
    
    if amount < 0:
        logger.error("Invalid amount detected", error_code="NEG_AMT")
```

## 7. Ecosystem Integration
The Observability component acts as a cross-cutting concern. It integrates deeply with the **Web Transports** (to automatically log incoming requests and response codes) and the **CQRS Bus** (to trace when events are published or consumed). It is strictly considered an anti-pattern to use the standard Python `logging` module directly without going through this component, as you will lose context variables and correlation tracking.
