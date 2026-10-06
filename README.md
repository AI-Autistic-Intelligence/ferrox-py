# ⚡ Ferrox-Py (Core Framework)

<p align="center">
  <b>A Python 3.11+ Framework for Enterprise Server-Side Development</b><br/>
  <i>Inspired by the robustness of Rust-Ferrox, bringing Inversion of Control, Modularity, and Onion Architecture to the Python ecosystem.</i>
</p>

---

## 1. Overview (What does this do?)
`ferrox-py` is the core foundation of the Ferrox ecosystem for Python. It provides an Inversion of Control (IoC) container, a Dependency Injection (DI) system, and the fundamental structure required to develop robust, scalable, and decoupled backend applications in Python. It goes beyond being just a web framework; it serves as a complete application lifecycle manager that supports REST APIs, GraphQL, background jobs, event queues, and advanced distributed concurrency controls.

## 2. Philosophy (Why does it exist?)
Modern backend development in Python is often plagued by monolithic scripts or overly permissive frameworks, causing architectural decisions to fragment over time. Ferrox-Py was created to mitigate the technical debt inherent in complex projects by enforcing:
- **Strict Decoupling** between domain logic (Business Layer) and the transport protocol (HTTP, gRPC, Queues).
- **Secure State Management** through centralized IoC containers.
- **Rigorous Validation** upon entry (leveraging Pydantic).
- **Absolute Resilience** by enforcing Distributed Locks, Circuit Breakers, and genuine End-to-End (E2E) testing capabilities.

## 3. Target Audience (Who is it for?)
This framework is specifically designed for **Data Platforms**, **Enterprise SaaS**, and **Microservices Architectures** where security, code predictability, state idempotency, and long-term maintainability are absolutely critical. If you need a system that seamlessly scales alongside your team without degrading into a convoluted "spaghetti code" architecture, Ferrox-Py is the ideal choice.

## 4. Architecture (How does it work?)
Ferrox-Py faithfully adopts the **7-Layer Onion Request Pipeline** from the original Ferrox ecosystem, while integrating enterprise resilience:
1. **Security & Headers**: Initial interception and sanitization of incoming requests.
2. **Active Defense & Rate Limiting**: Preemptive protection against system abuse (with Distributed Rate Limiting).
3. **Auth Guards**: Extraction and strict validation of authentication tokens (JWT/PASETO).
4. **RBAC & ZK Proofs**: Rigorous Role-Based Access Control and zero-knowledge mechanisms.
5. **Validation Pipe**: Formal checking of the DTO (Data Transfer Object) payload.
6. **Controller Layer**: Translation of the transport protocol into the specific domain language (protected by Singleflight and Circuit Breakers).
7. **Business Service / CQRS**: Execution of domain logic, state mutations, and persistence via Saga Orchestrators.

## 5. Installation / Setup
To run `ferrox-py`, ensure you have an environment with **Python 3.11+**. No prior configuration is required, but it is highly recommended to use a virtual environment.

```bash
# Example local installation (development mode)
pip install ferrox-py
```
For Enterprise E2E testing against real databases, the framework ships with a comprehensive Docker Compose setup:
```bash
# Start Redis, MongoDB, and PostgreSQL for true integration tests
docker-compose up -d
pytest tests/e2e -v
```

## 6. Quickstart (Usage)
Below is a minimal setup using Python 3.11+ to initialize the application and leverage distributed systems:

```python
import asyncio
from ferrox_py.core.app import FerroxApp
from ferrox_py.core.container import Container
from ferrox_py.security.distributed_locks import DistributedLockManager

async def main():
    # Initialize the IoC container
    container = Container()
    
    # Retrieve distributed components (e.g., Redis-backed Lock Manager)
    lock_manager = container.resolve(DistributedLockManager)
    
    # Safely acquire an atomic lock to prevent race conditions
    async with lock_manager.acquire("my-atomic-lock", ttl_ms=5000):
        print("Exclusive lock acquired! Safely executing distributed logic...")
    
    # Build and start the Ferrox application
    app = FerroxApp(container)
    app.start()

if __name__ == "__main__":
    asyncio.run(main())
```

## 7. Ecosystem Integration
The Core module is intentionally designed to act as a hub that can be seamlessly extended by specialized packages:
- 🛠️ **ferrox-py-utils**: Integration for ETL tools, data pipelines, and connectors (e.g., S3, CSV).
- 🔒 **ferrox-py-auth**: Integrates IAM, SSO, RBAC, and GDPR compliance features directly into the Auth Guards layer.
- 💳 **ferrox-py-commerce**: Interfaces with Stripe/PayPal webhooks and enforces idempotency in the Transaction State.
