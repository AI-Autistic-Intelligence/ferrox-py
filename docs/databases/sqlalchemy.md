# SQLAlchemy Integration

## 1. Overview (What does this do?)
The SQLAlchemy module provides a native, pre-configured wrapper for `SQLAlchemy` (v2) inside the `ferrox-py` ecosystem. It handles asynchronous database connections, session management per-request, and exposes an abstract repository layer for executing SQL queries smoothly without boilerplates.

## 2. Philosophy (Why does it exist?)
Configuring SQLAlchemy correctly for highly concurrent, asynchronous Python applications is notoriously tricky, often resulting in `DetachedInstanceError` or connection pool exhaustion. This module abstracts away engine creation and session teardown, enforcing best practices. By coupling SQLAlchemy tightly with the Dependency Injection container, developers never have to pass `session` objects manually across their application tiers.

## 3. Target Audience (Who is it for?)
This is designed for backend developers utilizing relational databases (PostgreSQL, MySQL, SQLite) who want to leverage the power of SQLAlchemy 2.0's async capabilities while adhering to the Repository pattern required by `ferrox-py`'s Domain-Driven Design principles.

## 4. Architecture (How does it work?)
- **AsyncDatabaseService**: Acts as the singleton engine provider. It initializes the SQLAlchemy `create_async_engine` with optimal pool sizes and timeouts based on environment variables.
- **Session Scoping**: A middleware automatically opens an async `Session` at the start of an HTTP request and safely commits/rolls back and closes it at the end of the request.
- **BaseRepository**: An abstract class that takes the active `Session` and provides generic CRUD operations (`create`, `update`, `delete`, `find_by_id`).

## 5. Installation / Setup
To use this module, you must install `ferrox-py` along with SQLAlchemy and the appropriate async database driver (like `asyncpg` for PostgreSQL).

```bash
pip install sqlalchemy asyncpg
```

## 6. Quickstart (Usage)
```python
from ferrox_py.databases.sql import AsyncDatabaseService
from ferrox_py.databases.sql.repository import BaseRepository
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String)

class UserRepository(BaseRepository):
    # This class inherits async CRUD operations automatically
    pass

# The engine and session injection are handled by the container:
# container.register("db_service", AsyncDatabaseService(url="postgresql+asyncpg://..."))
```

## 7. Ecosystem Integration
The SQLAlchemy module is deeply integrated into the **Data Component**. It plays perfectly with the **CQRS Bus**, allowing Command Handlers to execute complex, multi-table transactions natively while being oblivious to the underlying connection management logic handled by the Core framework.
