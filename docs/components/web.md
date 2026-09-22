# Web & Transports Component

Il modulo web di `ferrox-py` non impone FastAPI, sebbene sia fortemente consigliato per la validazione automatica dei tipi. Invece, funge da proxy agnostico (API Gateway / Transport Layer).

## 1. Architettura Multi-Trasporto
`ferrox-py` supporta l'esecuzione simultanea di più trasporti (server) nello stesso ciclo di vita:
- **HTTP REST / API Gateway**: Gestione classica con decoratori.
- **WebSockets / SSE (Server-Sent Events)**: Stream real-time gestiti da router specializzati.
- **GraphQL**: Schema generati e integrati (ad es. Strawberry o Graphene).

## 2. Decorators & Pipes
Ogni endpoint beneficia dei decoratori integrati che eseguono logiche *prima* che l'handler venga invocato (Onion Request Pipeline).
- `@require_roles("admin")`: Controlla il RBAC.
- `@validate_schema(MyPydanticModel)`: Valida il body e lancia eccezioni `400 Bad Request` in caso di difetto.

## 3. Custom Transports
Se un servizio richiede un protocollo speciale (es. TCP Raw o file-based trigger), l'implementazione del trasporto base (`ferrox_py.transports.base`) permette di inserire il nuovo server nell'Application loop.

```python
# Aggiungere un datagrid parser alle tue route
from ferrox_py.transports.datagrid import parse_ag_grid_query

# Il request url "/users?sort=name:asc" viene parsato e mappato per SQLAlchemy automaticamente
query_opts = parse_ag_grid_query(request.url)
```
