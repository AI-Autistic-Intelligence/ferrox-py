# Core Component (Inversion of Control)

## 1. Overview (What does this do?)
The Core component is the absolute backbone of the `ferrox-py` framework. It manages the entire lifecycle of the application, utilizing a robust Inversion of Control (IoC) container to instantiate, wire, and manage all services, databases, and dependencies.

## 2. Philosophy (Why does it exist?)
Unlike lightweight web frameworks (such as raw FastAPI or Flask) where application state is often passed around as global variables, singletons, or function parameters, `ferrox-py` strictly enforces the use of an IoC container. This philosophy prevents spaghetti code, makes unit testing incredibly simple (by easily mocking injected dependencies), and ensures that the lifecycle of complex objects (like Database connection pools) is predictably managed by the framework, not the developer.

## 3. Target Audience (Who is it for?)
This core module is meant for backend developers who need a highly structured, predictable way to organize their business logic. It appeals heavily to developers coming from enterprise backgrounds (like Java Spring or TypeScript's NestJS) who miss structured Dependency Injection in the Python ecosystem.

## 4. Architecture (How does it work?)
The Architecture relies on the `ferrox_py.core.container.Container` class, which acts as a thread-safe registry. 
Dependencies are registered either by string name or directly by class type. Currently, the IoC prioritizes **Singleton** resolution. To minimize boot time overhead, dependencies are **Lazy Loaded**—they are only instantiated the very first time they are resolved. The `FerroxApp` class accepts this container and handles Lifecycle Hooks (Start, Stop, Crash), initializes the 7-Layer Request Pipeline, and binds transports (HTTP, WebSockets).

## 5. Installation / Setup
The Core IoC module is included by default when you install the `ferrox-py` base package. No additional libraries are required for the fundamental Dependency Injection to function.

## 6. Quickstart (Usage)
```python
from ferrox_py.core.container import Container

class Database:
    def execute(self):
        return "Query Executed"

class UserService:
    # Dependencies are explicitly required in the constructor
    def __init__(self, db: Database):
        self.db = db

# 1. Initialization
container = Container()
container.register("db", Database())

# 2. Dependency resolution and wiring
# The container provides the 'db' instance to UserService
container.register("user_service", UserService(db=container.resolve("db")))

# 3. Usage
service = container.resolve("user_service")
print(service.db.execute())
```

## 7. Ecosystem Integration
The Core module integrates with the concept of **Providers and Modules** (inspired by NestJS). Specific features are encapsulated inside Modules (e.g., `AuthModule`), which define an array of Providers (classes) that are automatically registered into the Container. This ensures seamless integration with every other component in the `ferrox-py` ecosystem, decoupling domain logic from infrastructure.
