# Security Component

## 1. Overview (What does this do?)
The Security module implements layered defense for `ferrox-py` applications. It provides native, out-of-the-box protection against common attack vectors (like DDoS or brute force), enforces cryptographic token validation, and manages secure, distributed state locks.

## 2. Philosophy (Why does it exist?)
Security cannot be an afterthought in enterprise software. Instead of relying on developers to remember to add rate limiting or sanitize headers on every route, `ferrox-py` enforces these protections at the pipeline level. Furthermore, it advocates for modern cryptographic standards (like PASETO) to avoid the historical vulnerabilities associated with standard JWT implementations.

## 3. Target Audience (Who is it for?)
This component is essential for security engineers, system architects, and developers building publicly exposed APIs, Financial Technology (FinTech) services, or applications handling Personally Identifiable Information (PII) that require rigorous compliance and threat mitigation.

## 4. Architecture (How does it work?)
- **Moving Target Defense (MTD) & Sanitization**: HTTP responses are sanitized (e.g., stripping `X-Powered-By`) and armed with strict HSTS and CSP headers by default.
- **Distributed Rate Limiting**: Built on top of Redis using a sliding window token bucket algorithm to mitigate DDoS and brute-force attacks by limiting requests per IP or API Key.
- **Advanced Auth (PASETO/JWT)**: The Auth Guards securely extract, verify, and decode Platform-Agnostic Security Tokens (PASETO) or standard JWTs before the request reaches the controller.
- **Self-Auditing (WSTG Auditor)**: The `SecuritySelfTest` class allows the application to audit its own environment upon booting (e.g., checking file permissions, TLS configurations, and secret entropy).
- **Distributed Locks**: Utilizes Redis (Redlock algorithm) to prevent race conditions in clustered environments.

## 5. Installation / Setup
Security abstractions are built-in, but to utilize distributed features like Rate Limiting and Redlock, a Redis server and the corresponding python driver are required. PASETO support requires external cryptographic libraries.

```bash
pip install redis pyseto
```

## 6. Quickstart (Usage)
Generating and validating a secure PASETO token:

```python
from ferrox_py.security.paseto import PasetoTokenService
from ferrox_py.security.distributed_locks import RedisLock

# 1. Token Generation
token_service = PasetoTokenService(secret_key=b"super-secret-key-must-be-32-bytes!")
token = token_service.generate({"user_id": 1, "role": "admin"})

# 2. Distributed Locking
def recharge_wallet(redis_client, user_id: int):
    # Prevents concurrent requests from race-conditioning the wallet balance
    with RedisLock(redis_client, f"recharge_wallet_lock_{user_id}"):
        # Safe critical section
        pass
```

## 7. Ecosystem Integration
The Security module is the absolute core of the **7-Layer Request Pipeline**, specifically managing Layers 1 (Security Headers), 2 (Rate Limiting), 3 (Sentinel Threat Engine), and 4 (Auth Guards). It relies on the **Data Component** (specifically the Redis wrappers) to maintain distributed state for rate limiters and locks.
