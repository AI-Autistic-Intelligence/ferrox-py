# Distributed Circuit Breaker

## 1. Overview (What does this do?)
The Distributed Circuit Breaker acts as a protective shield for external service integrations (e.g., third-party APIs, microservices, databases). It dynamically monitors the failure rates of outgoing requests. If a specific provider starts failing continuously, the Circuit Breaker "opens" and immediately halts all further requests to that service for a specified cooldown period, returning an error instantly without waiting for a timeout.

## 2. Philosophy (Why does it exist?)
The core philosophy is fail-fast resilience. When a downstream dependency degrades, continuing to hammer it with requests not only slows down the calling application due to hanging threads, but it can also cause cascading failures across the entire cluster. By cutting the circuit early and distributing the state globally via Redis, all instances of your application simultaneously stop overwhelming the degraded service, allowing it time to recover.

## 3. Target Audience (Who is it for?)
This feature is designed for backend engineers integrating fragile third-party APIs, legacy systems, or distributed microservices. It is crucial for high-availability architectures where a slow external API must never be allowed to exhaust the connection pools or worker threads of the main application.

## 4. Architecture (How does it work?)
The `DistributedCircuitBreaker` uses Redis to maintain global state. It operates using a classic state machine:
- **CLOSED**: Requests flow normally. Failures are counted.
- **OPEN**: If failures exceed `max_failures`, the circuit opens. Requests are instantly rejected with a `CircuitBreakerOpenException`.
- **HALF-OPEN**: After `reset_timeout`, the circuit permits a single test request. If it succeeds, the circuit closes; if it fails, the circuit re-opens and resets the timeout.

## 5. Installation / Setup
The Circuit Breaker is included natively in `ferrox-py`. Because it is distributed, it strictly relies on Redis to synchronize the failure state across all running application pods.

```bash
pip install ferrox-py
```
You need a healthy Redis connection injected into the `DistributedCircuitBreaker`.

## 6. Quickstart (Usage)
```python
from ferrox_py.resilience.circuit_breaker import DistributedCircuitBreaker, CircuitBreakerOpenException
import redis.asyncio as redis

async def main():
    client = redis.from_url("redis://localhost")
    cb = DistributedCircuitBreaker(client, max_failures=3, reset_timeout=30)

    async def fetch_third_party():
        raise ValueError("Service Unavailable")

    try:
        # Will attempt to call, but after 3 consecutive errors across any pod,
        # the circuit will open globally for the 'stripe_api' provider.
        await cb.call("tenant_123", "stripe_api", fetch_third_party)
    except CircuitBreakerOpenException:
        print("Circuit is open! Falling back to cache or aborting early.")
```

## 7. Ecosystem Integration
The Circuit Breaker integrates deeply with the **Integration Connectors** found in `ferrox-py-utils`. Specifically, the `@connector_policy` decorator automatically wraps outbound I/O in a Circuit Breaker logic block. It also alerts the **Observability** suite, logging critical warnings when a circuit opens so DevOps engineers are immediately notified of external degradation.
