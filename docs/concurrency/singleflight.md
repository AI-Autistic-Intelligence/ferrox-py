# Singleflight Concurrency

## 1. Overview (What does this do?)
The `SingleflightManager` is a highly specialized concurrency utility designed to suppress duplicate function executions. When multiple identical requests are triggered at the exact same time (e.g., fetching the same database record), Singleflight intercepts them. It allows only the *first* request to actually execute the heavy I/O operation, while the subsequent identical requests simply wait. Once the first request finishes, its result is automatically shared with all waiting callers.

## 2. Philosophy (Why does it exist?)
The primary philosophy of Singleflight is Cache Stampede prevention (also known as a thundering herd). When a popular cache key expires, thousands of concurrent requests might hit the server simultaneously, forcing the database to process the same heavy query thousands of times in parallel, leading to an immediate database crash. Singleflight guarantees that regardless of how many concurrent requests ask for the same data, the database is queried exactly once.

## 3. Target Audience (Who is it for?)
This is a critical performance optimization tool for backend engineers building high-traffic, read-heavy platforms (like media catalogs, dashboards, and live trading platforms). It is meant for systems where massive spikes in identical traffic are expected and must be absorbed gracefully without scaling the database hardware.

## 4. Architecture (How does it work?)
The `SingleflightManager` is implemented completely in-memory using `asyncio` primitives (Promises/Futures).
1. When `manager.do("key_A", task)` is called, it checks a local dictionary.
2. If `"key_A"` does not exist, it creates a new `asyncio.Future`, stores it, and begins executing the `task`.
3. If another request calls `manager.do("key_A", task)` while the first is still running, it receives the exact same `Future` and simply `awaits` it.
4. When the first task resolves, the `Future` is fulfilled, propagating the result simultaneously to all waiters, and the key is cleaned up.

## 5. Installation / Setup
Singleflight is purely algorithmic and relies exclusively on native Python `asyncio`. It requires zero external dependencies, no Redis, and no configuration.

```bash
pip install ferrox-py
```
It is readily available in the `ferrox_py.concurrency` module.

## 6. Quickstart (Usage)
```python
import asyncio
from ferrox_py.concurrency.singleflight import SingleflightManager

manager = SingleflightManager()

async def heavy_database_query():
    print("-> Querying database... (This should only print ONCE)")
    await asyncio.sleep(2)
    return {"data": "cached_payload"}

async def worker(worker_id):
    result = await manager.do("dashboard_stats", heavy_database_query)
    print(f"Worker {worker_id} received: {result}")

async def main():
    # Simulate 5 concurrent requests asking for the exact same data instantly
    await asyncio.gather(
        worker(1), worker(2), worker(3), worker(4), worker(5)
    )

if __name__ == "__main__":
    asyncio.run(main())
```

## 7. Ecosystem Integration
Singleflight is the invisible shield of the **Controllers** (Layer 6) and **Business Services** (Layer 7). It works elegantly alongside the **CQRS** query handlers. By wrapping complex read queries inside a Singleflight key, the Ferrox ecosystem natively guarantees absolute protection against cache stampedes without requiring the developer to manually manage complex Redis caching logic.
