# Task Scheduling

## 1. Overview (What does this do?)
The Task Scheduling architecture in Ferrox-Py provides a built-in mechanism for running background jobs, recurrent tasks, and deferred asynchronous operations outside of the main HTTP request-response cycle. It allows developers to define cron-like schedules or simple fire-and-forget background workers securely within the Inversion of Control (IoC) context.

## 2. Philosophy (Why does it exist?)
Modern web applications frequently need to perform long-running tasks—such as sending batch emails, generating reports, or cleaning up stale database records. Blocking an HTTP thread to perform these operations leads to poor UX and timeouts. The Task Scheduling module exists to offload this work cleanly without requiring developers to immediately configure external dependencies like Celery or Redis for simple scheduling needs.

## 3. Target Audience (Who is it for?)
This module is intended for backend engineers who need to execute periodic maintenance tasks or offload heavy I/O operations from their API endpoints securely, maintaining access to the application's configured IoC container and database connections.

## 4. Architecture (How does it work?)
The task scheduler runs as a background asyncio loop, spawned alongside the main web server by `FerroxApp`. Tasks registered via the `@cron` or `@background` decorators are collected at startup. When a scheduled time is reached, the scheduler spawns a managed task, automatically injecting any required dependencies (like a Database connection or Logger) from the central IoC Container before executing the business logic.

## 5. Installation / Setup
Task scheduling is built directly into the core `ferrox-py` package. No additional message brokers (like RabbitMQ) are necessary for the default memory-based scheduler. For distributed task locking across multiple server nodes, an optional Redis integration can be configured.

## 6. Quickstart (Usage)
You can easily register a recurrent job using the `@cron` decorator. The scheduler will parse standard cron expressions.

```python
from ferrox_py.core.scheduling import cron
from ferrox_py.core.container import Container

class CleanupService:
    @cron("*/5 * * * *")  # Runs every 5 minutes
    async def remove_stale_sessions(self):
        print("Cleaning up stale database sessions...")
        # Dependency injection works here automatically if the class is resolved via IoC

# Register the service in the container so the scheduler can find it
container = Container()
container.register("cleanup_service", CleanupService)
```

## 7. Ecosystem Integration
The Task Scheduling module interacts heavily with the Observability components. Every background task execution generates trace IDs and metrics, which are logged automatically. If a background job fails, it integrates with the centralized error handler to send alerts (e.g., triggering a webhook to a Slack channel) without bringing down the main API server.
