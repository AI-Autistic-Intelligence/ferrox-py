# Data Component

Il modulo `ferrox-py.databases` astrae le connessioni ai database relazionali e non relazionali, fornendo pool di connessioni e classi base per i Repository.

## 1. SQL (SQLAlchemy)
Integrazione nativa e pulita con `SQLAlchemy` (V2) asincrono. Fornisce:
- Engine Async singleton e Connection Pooling.
- Gestione trasparente delle sessioni.
- Repository pattern astratto (`BaseRepository`) con metodi `find_by_id`, `create`, `update`, `delete`.

### Esempio BaseRepository
```python
class SqlUserRepository(BaseRepository):
    # Eredita e implementa i metodi custom
    pass
```

## 2. NoSQL (MongoDB)
Wrapper ottimizzato sopra `motor` (l'estensione asincrona di pymongo). 
- Supporta serializzazione nativa Pydantic <-> BSON.
- Query asincrone.

## 3. Caching & Idempotency (Redis)
Il wrapper Redis integrato (usato in `ferrox-py-commerce` e `security`) è essenziale per:
- Lock distribuiti e Singleflight.
- Rate limiting.
- Memorizzazione di stati temporanei (State Machines).
- Caching di query frequenti.

## 4. Migrations
Gestione delle migrazioni unificata. Integra Alembic dietro le quinte per applicare le revisioni del database programmaticamente all'avvio dell'applicazione (`FerroxApp`), assicurando che il backend e il database siano sempre allineati (Zero-Downtime schema upgrades).
