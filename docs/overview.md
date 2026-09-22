# Overview

## 1. Philosophy / Purpose
Ferrox-Py provides the 7-Layer Onion Request Pipeline defined by the Ferrox ecosystem, adapted for enterprise Python 3.11+.

## 2. Architectural Layering
1. Security Header Enforcer Middleware
2. Polymorphic Route Token (MTD)
3. Sentinel Threat Engine
4. Auth Guards (PASETO v4)
5. Validation Pipe (Pydantic)
6. Controller Route Handler (FastAPI)
7. Business Service (Singleflight / CQRS)

## 3. How it Works (Under the hood)
It uses FastAPI as the base ASGI container and layers Ferrox-specific security modules as middleware and dependencies.

## 4. Why it was designed this way
To ensure maximum zero-trust security and prevent cache stampedes in a highly concurrent environment.

## 5. Usage Guide & Code Examples
```python
from ferrox_py.core.app import FerroxApp

app = FerroxApp()
```

## 6. Anti-Patterns
Skipping layers or writing raw Starlette middleware bypassing the pipeline.

## 7. Pro-Tips / Best Practices
Always use singleflight in the business layer for I/O bounds.
