# ⚡ Ferrox-Py (Core Framework)

<p align="center">
  <b>A Python 3.11+ Framework for Enterprise Server-Side Development</b><br/>
  <i>Inspired by the robustness of Rust-Ferrox, bringing Inversion of Control, Modularity, and Onion Architecture to the Python ecosystem.</i>
</p>

---

## 1. Overview (What does this do?)
`ferrox-py` is the core foundation of the Ferrox ecosystem for Python. It provides an Inversion of Control (IoC) container, a Dependency Injection (DI) system, and the fundamental structure required to develop robust, scalable, and decoupled backend applications in Python. It goes beyond being just a web framework; it serves as a complete application lifecycle manager that simultaneously supports REST APIs, GraphQL, background jobs, and event queues.

## 2. Philosophy (Why does it exist?)
Modern backend development in Python is often plagued by monolithic scripts or overly permissive frameworks, causing architectural decisions to fragment over time. Ferrox-Py was created to mitigate the technical debt inherent in complex projects by enforcing:
- **Strict Decoupling** between domain logic (Business Layer) and the transport protocol (HTTP, gRPC, Queues).
- **Secure State Management** through centralized IoC containers.
- **Rigorous Validation** upon entry (leveraging Pydantic).
- **Mitigation of Abuse** by strictly separating side effects and enforcing robust architectural boundaries.

## 3. Target Audience (Who is it for?)
This framework is specifically designed for **Data Platforms**, **Enterprise SaaS**, and **Microservices Architectures** where security, code predictability, and long-term maintainability are absolutely critical. If you need a system that seamlessly scales alongside your team without degrading into a convoluted "spaghetti code" architecture, Ferrox-Py is the ideal choice.

## 4. Architecture (How does it work?)
Ferrox-Py faithfully adopts the **7-Layer Onion Request Pipeline** from the original Ferrox ecosystem:
1. **Security & Headers**: Initial interception and sanitization of incoming requests.
2. **Active Defense & Rate Limiting**: Preemptive protection against system abuse.
3. **Auth Guards**: Extraction and strict validation of authentication tokens (JWT/PASETO).
4. **RBAC & ZK Proofs**: Rigorous Role-Based Access Control and zero-knowledge mechanisms.
5. **Validation Pipe**: Formal checking of the DTO (Data Transfer Object) payload.
6. **Controller Layer**: Translation of the transport protocol into the specific domain language.
7. **Business Service / CQRS**: Execution of domain logic, state mutations, and persistence.

## 5. Installation / Setup
To run `ferrox-py`, ensure you have an environment with **Python 3.11+**. No prior configuration is required, but it is highly recommended to use a virtual environment.

```bash
# Example local installation (development mode)
pip install -e .
```
The project also exposes the `ferrox` CLI for utilities and basic administrative tasks.

## 6. Quickstart (Usage)
Below is a minimal setup using Python 3.11+ to initialize the application and its dependency container:

```python
from ferrox_py.core.app import FerroxApp
from ferrox_py.core.container import Container

def main():
    # Initialize the IoC container
    container = Container()
    
    # Register your services and controllers here
    # container.register("my_service", MyService)
    
    # Build and start the Ferrox application
    app = FerroxApp(container)
    app.start()

if __name__ == "__main__":
    main()
```

## 7. Ecosystem Integration
The Core module is intentionally designed to act as a hub that can be seamlessly extended by specialized packages:
- 🛠️ **ferrox-py-utils**: Integration for ETL tools, data pipelines, and connectors (e.g., S3, CSV).
- 🔒 **ferrox-py-auth**: Integrates IAM, SSO, RBAC, and GDPR compliance features directly into the Auth Guards layer.
- 💳 **ferrox-py-commerce**: Interfaces with Stripe/PayPal webhooks and enforces idempotency in the Transaction State.
