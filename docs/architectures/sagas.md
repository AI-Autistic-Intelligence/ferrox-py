# Saga Orchestrator

## 1. Overview (What does this do?)
The Saga Orchestrator provides a robust mechanism to manage long-running, distributed transactions across multiple microservices or database domains. Instead of relying on traditional 2PC (Two-Phase Commit) protocols which lock resources and reduce throughput, it breaks a transaction down into a series of local `SagaStep`s. If any step fails, the orchestrator automatically triggers the corresponding compensation (rollback) logic for all previously succeeded steps.

## 2. Philosophy (Why does it exist?)
In an enterprise microservice architecture, eventual consistency is paramount. Network failures, database timeouts, and logical errors are inevitable. The philosophy of the Saga Orchestrator is absolute reliability in failure scenarios. By persisting the state of each transaction in a central repository (e.g., Redis) before execution, it ensures that no transaction is left in an unknown or hanging state, completely eliminating data corruption across boundaries.

## 3. Target Audience (Who is it for?)
This module is intended for backend architects dealing with cross-domain mutations—such as processing an e-commerce checkout where payment, inventory deduction, and email notification must all succeed or all gracefully roll back. It is critical for systems where ACID compliance cannot be guaranteed natively by a single database instance.

## 4. Architecture (How does it work?)
The architecture revolves around three core components:
1. **SagaStep**: A discrete unit of work defining both an `execute` function and an optional `compensate` function.
2. **SagaStateRepository**: A persistent layer (usually Redis-backed via `RedisSagaStateRepository`) that records the status (`PENDING`, `COMPLETED`, `COMPENSATED`, `FAILED`) of the saga and its internal steps.
3. **SagaOrchestrator**: The execution engine that sequentially resolves each `SagaStep`. If an exception is raised, it catches the error, halts forward progress, and retroactively triggers the compensation functions in reverse order.

## 5. Installation / Setup
The Saga Orchestrator is a core component of `ferrox-py`. It does not require extra packages, though the `RedisSagaStateRepository` specifically requires `redis.asyncio` (which is already included as an optional or core dependency).

```bash
pip install ferrox-py
```
Ensure your Redis instance is running and accessible to store saga states during execution.

## 6. Quickstart (Usage)
```python
from ferrox_py.architectures.sagas import SagaOrchestrator, SagaStep, RedisSagaStateRepository
import redis.asyncio as redis

async def run_saga():
    client = redis.from_url("redis://localhost")
    repo = RedisSagaStateRepository(client)
    orchestrator = SagaOrchestrator(repo)

    async def charge_card(state):
        return "Charged $100"

    async def refund_card(state):
        print("Compensating: Refunded $100")

    async def ship_item(state):
        raise ValueError("Item out of stock!")

    steps = [
        SagaStep("charge", charge_card, refund_card),
        SagaStep("ship", ship_item)
    ]

    try:
        await orchestrator.execute(steps)
    except Exception as e:
        print(f"Saga failed and compensated: {e}")
```

## 7. Ecosystem Integration
The Saga Orchestrator perfectly pairs with the **CQRS** (Command Query Responsibility Segregation) module. Typically, a Command Handler will instantiate a Saga to perform multi-step data mutations. Furthermore, the orchestrator utilizes the **Observability** suite (Tracing) to ensure that if a compensation occurs, the entire timeline is clearly visible in Grafana or Jaeger.
