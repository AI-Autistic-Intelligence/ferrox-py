# Data Component

## 1. Overview (What does this do?)
The `ferrox-py.databases` module abstracts connections to both relational and non-relational databases. It provides robust connection pooling, session management, schema migrations, and base classes for implementing the Repository pattern cleanly across different storage engines.

## 2. Philosophy (Why does it exist?)
Database interactions are often the biggest bottleneck and source of technical debt in web applications. This component exists to provide a uniform, asynchronous, and safe way to interact with databases without scattering raw SQL or driver-specific code throughout the business logic. It enforces the Repository pattern, ensuring that the domain layer remains entirely agnostic to the underlying storage mechanism.

## 3. Target Audience (Who is it for?)
This component is for backend developers who need reliable, scalable database connectivity. Whether you are using SQL for structured relational data, MongoDB for flexible documents, or Redis for high-speed caching and locking, this module provides the necessary enterprise-grade abstractions.

## 4. Architecture (How does it work?)
- **SQL (SQLAlchemy)**: Native integration with asynchronous SQLAlchemy V2. It provides a Singleton Async Engine, transparent session lifecycle management (often tied to the request lifecycle), and an abstract `BaseRepository` with standard CRUD methods.
- **NoSQL (MongoDB)**: An optimized wrapper over `motor` (asynchronous PyMongo). It supports native serialization and deserialization between Pydantic models and BSON, along with async queries.
- **Caching & Idempotency (Redis)**: Integrated wrapper for distributed locks (Singleflight), rate limiting, caching, and state machines.
- **Migrations**: Unified migration management integrating Alembic behind the scenes, allowing programmatic schema upgrades during the `FerroxApp` boot sequence.

## 5. Installation / Setup
While the abstractions are native, you must install the underlying asynchronous drivers for the databases you intend to use.

```bash
# For PostgreSQL and SQLAlchemy
pip install asyncpg sqlalchemy alembic

# For MongoDB
pip install motor

# For Redis
pip install redis
```

## 6. Quickstart (Usage)
```python
from ferrox_py.databases.sql.repository import BaseRepository

# 1. Define your specific repository inheriting from the Base
class SqlUserRepository(BaseRepository):
    # Base CRUD methods (find_by_id, create, update, delete) are automatically inherited
    
    # Implement custom data access methods
    async def find_by_email(self, email: str):
        # Implementation using the injected async session
        pass

# 2. Register it in the IoC Container
# container.register("user_repo", SqlUserRepository(session=...))
```

## 7. Ecosystem Integration
The Data Component is universally utilized. It provides the foundation for the **AuthModule** (storing users and RBAC roles), the **Commerce** ecosystem (maintaining strict idempotency using Redis and transactional SQL for orders), and integrates with the **Core IoC** for injecting valid database sessions into the CQRS Command Handlers.
