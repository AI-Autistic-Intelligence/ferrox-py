# Security Component

Il modulo Security implementa la difesa a strati per le applicazioni `ferrox-py`, fornendo nativamente protezione contro attacchi comuni e validazione crittografica.

## 1. Moving Target Defense (MTD) e Introspection
Non limitarti a proteggere gli endpoint statici. Il modulo espone concetti avanzati:
- **Header Sanitization**: Le risposte vengono ripulite (niente `X-Powered-By`) e armate con HSTS e CSP stretti per default.
- **Rate Limiting Distribuito**: Basato su Redis, mitiga gli attacchi DDoS limitando la frequenza di richieste per IP (sliding window token bucket).

## 2. Advanced Auth (JWT & PASETO)
`ferrox-py` consiglia e supporta token PASETO (Platform-Agnostic Security Tokens) per evitare le vulnerabilità storiche e di design dei JWT standard (es. raggiri dell'algoritmo).

```python
from ferrox_py.security.paseto import PasetoTokenService

token_service = PasetoTokenService(secret_key=b"chiave-super-segreta-32-byte-lunga")
token = token_service.generate({"user_id": 1, "role": "admin"})
```

## 3. Selftest (WSTG Auditor)
La classe `SecuritySelfTest` permette al framework di fare auto-auditing. Al boot, è possibile avviare suite locali (ferrox-pentest-private) che scansionano:
- Permessi di file.
- Configurazioni HTTPS/TLS.
- Entropia delle variabili d'ambiente.
- Rate limits esposti.

## 4. Distributed Locks (Redlock)
Per evitare race conditions in ambiente distribuito, il modulo di sicurezza integra lock distribuiti:
```python
from ferrox_py.security.distributed_locks import RedisLock

with RedisLock(redis_client, "recharge_wallet_lock"):
    # Critical section sicura
    pass
```
