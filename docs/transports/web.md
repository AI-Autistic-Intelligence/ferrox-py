# Web & Transports Component

## 1. Overview (What does this do?)
The Web component in `ferrox-py` acts as an agnostic API Gateway and Transport Layer. It is responsible for parsing incoming network requests across multiple protocols, passing them through the strict 7-Layer Onion Pipeline, and routing them to the appropriate application Controllers.

## 2. Philosophy (Why does it exist?)
Many frameworks tightly couple their business logic to HTTP abstractions (like raw `request` objects). `ferrox-py`'s philosophy is to treat the transport layer as merely a delivery mechanism. Whether a command arrives via an HTTP REST call, a WebSocket message, or a GraphQL query, the underlying business logic remains completely isolated and agnostic to the network protocol.

## 3. Target Audience (Who is it for?)
This module is for developers building multi-protocol APIs. If your application needs to expose a traditional REST API for mobile clients, a GraphQL endpoint for internal frontends, and WebSockets for real-time notifications—all sharing the exact same business logic—this component manages that complexity safely.

## 4. Architecture (How does it work?)
- **Multi-Transport Architecture**: The application can run multiple servers (transports) simultaneously within the same asyncio event loop.
- **REST / API Gateway**: While agnostic, it strongly integrates with FastAPI as the default HTTP engine to leverage automatic OpenAPI schema generation and Pydantic type validation.
- **WebSockets / SSE**: Specialized routers handle real-time streaming and Server-Sent Events.
- **Decorators**: The component provides unified decorators (`@require_roles`, `@validate_schema`) that inject logic *before* the handler runs, regardless of the underlying transport.
- **Custom Transports**: Developers can implement the `ferrox_py.transports.base` interface to add entirely new triggers (e.g., raw TCP servers, message queue consumers, or file-system watchers).

## 5. Installation / Setup
To run the default HTTP REST gateway, FastAPI and an ASGI server (like Uvicorn) are required. GraphQL support requires additional libraries like Strawberry.

```bash
pip install fastapi uvicorn pydantic
# Optional: pip install strawberry-graphql
```

## 6. Quickstart (Usage)
Defining a controller and applying decorators:

```python
from ferrox_py.web.decorators import require_roles, validate_schema
from pydantic import BaseModel

class UserPayload(BaseModel):
    name: str

# These decorators hook into the Onion Pipeline automatically
@require_roles("admin")
@validate_schema(UserPayload)
async def create_user_handler(payload: UserPayload):
    # At this point, the user is an admin and the payload is guaranteed valid
    return {"message": f"User {payload.name} created successfully."}

# Custom utilities are also provided, e.g., parsing DataGrid queries:
from ferrox_py.transports.datagrid import parse_ag_grid_query
# query_opts = parse_ag_grid_query(request.url)
```

## 7. Ecosystem Integration
The Web component is the entry point for external data and therefore integrates directly with the **Security** component (to evaluate headers and tokens), the **Pipes/Interceptors** (for validating schemas), and the **Observability** component (to extract and log Correlation IDs from incoming requests).
