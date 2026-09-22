# Fundamentals: Modules

## 1. Overview (What does this do?)
Modules in `ferrox-py` are the fundamental building blocks used to organize an application into cohesive blocks of functionality. They group together related Controllers, Providers (Services, Repositories), and exported dependencies into a single, importable unit.

## 2. Philosophy (Why does it exist?)
As applications grow, keeping all dependencies and routes in a single global file becomes unmaintainable. Inspired by architectural patterns seen in Angular and NestJS, the Module system exists to enforce bounded contexts. A Module encapsulates a specific domain (e.g., `BillingModule` or `UserModule`), making it completely self-contained and easily pluggable or removable from the main application without causing cascading breaks.

## 3. Target Audience (Who is it for?)
This abstraction is meant for all developers using `ferrox-py`. Whether you are writing a tiny microservice or a massive monolithic application, structuring your code into logical Modules is a mandatory best practice within the framework.

## 4. Architecture (How does it work?)
A Module is simply a Python class decorated with `@module`. The decorator accepts lists of `controllers` (which handle routing), `providers` (the business logic and data access classes), and `imports` (other modules this module depends on). When the `FerroxApp` boots, it recursively traverses these Modules, registering all discovered Providers into the global Inversion of Control (IoC) Container.

## 5. Installation / Setup
Modules are a core structural concept provided natively by the `ferrox_py.core` package. No external installations are necessary.

## 6. Quickstart (Usage)
```python
from ferrox_py.core.decorators import module
from .controllers import UserController
from .services import UserService
from .repositories import UserRepository

@module(
    controllers=[UserController],
    providers=[
        UserService,
        UserRepository
    ],
    imports=[] # Import other modules here if needed
)
class UserModule:
    """
    The UserModule encapsulates everything related to User management.
    """
    pass
```

## 7. Ecosystem Integration
Modules are the glue that holds the entire framework together. For example, if you want to add Authentication to your app, you simply import the `AuthModule` from the `ferrox-py-auth` package into your root `AppModule`. The framework will automatically register its Auth Guards, JWT services, and Webhooks into your container.
