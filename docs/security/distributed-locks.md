# Distributed Locks

## 1. Overview (What does this do?)
The `DistributedLockManager` provides distributed concurrency control across your entire infrastructure. It allows multiple isolated application instances to acquire mutually exclusive locks over a specific resource using a central Redis store. This guarantees that a critical block of code is only executed by one worker at any given time, globally.

## 2. Philosophy (Why does it exist?)
In modern horizontal scaling, relying on simple in-memory threading locks (`asyncio.Lock()`) is completely ineffective because applications run across dozens of independent pods. The philosophy of the `DistributedLockManager` is to provide mathematical certainty that race conditions (such as double-charging a user or processing a webhook twice simultaneously) are impossible, enforcing strict atomicity across physical machine boundaries.

## 3. Target Audience (Who is it for?)
This tool is vital for financial platforms, billing architectures, inventory management systems, and background job processors where executing a transaction concurrently is catastrophic. If your code deals with real money or critical mutable state, distributed locking is non-negotiable.

## 4. Architecture (How does it work?)
The lock manager implements an advanced asynchronous context manager utilizing Redis `SET NX PX` (Set if Not eXists with expiration). 
When an instance requests a lock:
1. It generates a unique identifier (nonce).
2. It attempts to acquire the key in Redis atomically.
3. If successful, it proceeds; if the lock is held, it blocks or retries until `timeout_ms` is exhausted, throwing a `FerroxError` upon timeout.
4. On release, it utilizes a Lua script to ensure it only deletes the lock if its unique nonce matches, preventing accidental release of locks acquired by other delayed workers.

## 5. Installation / Setup
Distributed Locks are available directly in the `ferrox_py.security` module. A Redis instance is mandatory for the global synchronization backbone.

```bash
pip install ferrox-py
```
Ensure your application provides a configured `redis.asyncio` client to the manager.

## 6. Quickstart (Usage)
```python
from ferrox_py.security.distributed_locks import DistributedLockManager
from ferrox_py.core.errors import FerroxError
import redis.asyncio as redis

async def process_payment(user_id: str):
    client = redis.from_url("redis://localhost")
    lock_manager = DistributedLockManager(client)
    
    lock_key = f"payment_processing:{user_id}"
    
    try:
        # Acquire lock for max 5000ms. Wait max 1000ms to get it.
        async with lock_manager.acquire(lock_key, ttl_ms=5000, timeout_ms=1000):
            print(f"Lock acquired for {user_id}. Executing transaction...")
            # Perform atomic business logic here
    except FerroxError:
        print("Another process is currently handling this user's payment!")
```

## 7. Ecosystem Integration
Distributed Locks are heavily leveraged by the **Commerce Module** (`ferrox-py-commerce`) to ensure Stripe and PayPal webhook idempotency, guaranteeing that an invoice is never fulfilled twice. It is also used by the **CQRS** bus to prevent concurrent processing of the exact same command hash in distributed environments.
