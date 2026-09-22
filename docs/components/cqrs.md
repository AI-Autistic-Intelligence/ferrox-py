# CQRS, Events, and Sagas Component

## 1. Overview (What does this do?)
The CQRS (Command Query Responsibility Segregation) component provides integrated patterns for separating read operations (Queries) from write operations (Commands). It also provides an Event Dispatcher for Event-Driven Architectures and supports Sagas for managing distributed transactions across multiple microservices or database boundaries.

## 2. Philosophy (Why does it exist?)
In complex Enterprise architectures and microservices, having Controllers directly call Repositories to mutate state leads to tightly coupled, hard-to-maintain code. By forcing mutations through a Command Bus and reads through a Query Bus, `ferrox-py` enforces a clear separation of concerns. This allows read paths to be optimized (e.g., using caching or read replicas) entirely independently of the write paths, and enables reactive event-driven flows.

## 3. Target Audience (Who is it for?)
This component is designed for advanced architects and developers building complex, highly scalable systems. It is specifically aimed at those implementing Domain-Driven Design (DDD) and those who need to orchestrate complex business transactions that span multiple services without relying on distributed two-phase commits.

## 4. Architecture (How does it work?)
- **Command/Query Bus**: Resolves incoming Commands/Queries to their registered Handlers.
- **Event Dispatcher**: An in-memory Pub/Sub bus where Publishers emit Events (e.g., `PaymentCompleted`) and Subscribers asynchronously react to them. It is designed to be easily extensible to external message brokers like Redis Pub/Sub or RabbitMQ.
- **Sagas**: A state machine engine that executes a sequence of local transactions. If one step fails, the Saga orchestrator automatically triggers compensating actions (rollbacks) for all previously successful steps.

## 5. Installation / Setup
The in-memory CQRS and Event buses are included natively in `ferrox-py`. For distributed messaging (e.g., RabbitMQ or Redis), additional specific driver packages must be installed and configured within the IoC Container.

## 6. Quickstart (Usage)
```python
from ferrox_py.cqrs.bus import CommandBus

# 1. Define the Command
class CreateOrderCommand:
    def __init__(self, item_id: str):
        self.item_id = item_id

# 2. Define the Handler logic (mocked)
class OrderService:
    def create_order(self, cmd: CreateOrderCommand):
        print(f"Order created for item {cmd.item_id}")
        return True

# 3. Registration and Dispatch
bus = CommandBus()
order_service = OrderService()

# Register the handler that knows how to process the Command
bus.register_handler(CreateOrderCommand, order_service.create_order)

# The API Controller simply dispatches the command
result = bus.dispatch(CreateOrderCommand(item_id="12345"))
```

## 7. Ecosystem Integration
CQRS integrates heavily with the **Data Component** (for actual persistence executed by the Handlers) and the **Pipes/Interceptors**. Specifically, a Validation Pipe is often attached to the Command Bus to ensure that every Command object is structurally valid before it ever reaches the Business Service layer.
