# Fundamentals: Providers

## 1. Overview (What does this do?)
Providers are the most basic unit of dependency in `ferrox-py`. Any class that contains business logic, data access logic, or helper utilities can be designated as a Provider. Once marked, it can be managed by the Inversion of Control (IoC) container and injected into other Providers or Controllers.

## 2. Philosophy (Why does it exist?)
The Provider concept exists to enforce Dependency Injection (DI). Instead of a class manually instantiating its dependencies (e.g., `self.db = Database()`), the framework "provides" those dependencies via the constructor. This inversion ensures that components remain loosely coupled, making it incredibly easy to swap out implementations (like replacing a real database with a mock database during unit testing).

## 3. Target Audience (Who is it for?)
Every developer writing business logic in `ferrox-py` uses Providers. If you are writing a Service, a Repository, a Factory, or an API Client, you are writing a Provider.

## 4. Architecture (How does it work?)
By decorating a class with `@injectable`, you signal to the framework that this class should be registered in the IoC Container. The container analyzes the type hints in the class's `__init__` method. When the Provider is requested, the container recursively resolves and injects all required dependencies. Providers can be scoped: `SINGLETON` (one instance per application lifecycle, which is the default) or `TRANSIENT` (a new instance is created every time it is injected).

## 5. Installation / Setup
Providers and the `@injectable` decorator are built into the core `ferrox_py.core` package. They require Python's native type hinting system to function correctly.

## 6. Quickstart (Usage)
```python
from ferrox_py.core.decorators import injectable
from ferrox_py.core.enums import ProviderScope

# 1. Define a dependency provider
@injectable(scope=ProviderScope.SINGLETON)
class EmailClient:
    def send(self, to: str, msg: str):
        pass

# 2. Define a provider that relies on the EmailClient
@injectable()
class NotificationService:
    # The container reads this type hint and injects EmailClient automatically
    def __init__(self, email_client: EmailClient):
        self.email_client = email_client
        
    def notify_user(self, user_email: str):
        self.email_client.send(user_email, "Welcome!")
```

## 7. Ecosystem Integration
Providers are intrinsically linked to **Modules**. A Provider is only active if it is registered in the `providers` array of a `@module`. They are also the fundamental building blocks consumed by the **CQRS Command Handlers** and the **Controller Layer** to execute actual domain logic.
