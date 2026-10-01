# Quantitative Data Platform - Programmer & User Handbook

## 1. Executive Summary

This handbook details the architecture, design decisions, and operational guidelines for the **Quantitative Data Platform**, the official Ferrox-Py reference application. 

As a Senior Engineer, my objective was not merely to demonstrate the syntax of Ferrox-Py, but to prove its capabilities under extreme, real-world conditions: **High-Frequency Trading (HFT) and Quantitative Market Data Ingestion**. In this domain, dropped WebSocket packets, unpredictable event-loop blocking, and security vulnerabilities directly translate to financial loss.

This application is built with a **zero-trust security model**, **ACID-compliant relational persistence**, and **highly concurrent asynchronous I/O**.

---

## 2. Architectural Blueprint

### 2.1 The Domain Problem
We must connect to high-throughput financial exchanges (e.g., Binance), subscribe to real-time order book depth and trade streams, normalize the payload, and persist it to a database. Concurrently, we must expose this data via secure REST and GraphQL endpoints for downstream quant teams, backtesting engines, and dashboards.

### 2.2 System Components
1. **Outer Boundary Layer (Ferrox-Py Framework)**
   - Built on top of **FastAPI/Starlette**, inheriting raw ASGI performance.
   - Encapsulates route definitions, HTTP parsing, and dependency injection.
2. **7-Layer Onion Middleware Pipeline**
   - **Sentinel Threat Engine (`SentinelThreatEngineMiddleware`)**: Every incoming request (REST or GraphQL) is intercepted. Payloads are subjected to Shannon entropy analysis, Regex heuristic signature matching (for SQLi, XSS, and LLM Prompt Injections).
   - **Authentication (`PASETO v4`)**: We abandoned JWT due to algorithm confusion vulnerabilities. PASETO v4 strictly enforces cryptographic claims locally.
3. **Ingestion Daemon (`binance_ingestor.py`)**
   - **WebSocket Client**: Uses the `websockets` library.
   - **Lifecycle Management**: Managed via Starlette's `@asynccontextmanager`. When the API boots, the ingestor spawns as an isolated background task.
   - **Resilience**: Implements exponential backoff and circuit breakers for exchange disconnects.
4. **Persistence Layer (PostgreSQL & SQLAlchemy 2.0)**
   - **Why SQL over Redis?** Initially designed with Redis streams, the architecture was migrated to strict PostgreSQL to guarantee ACID compliance for trade ledgers. Redis is excellent for volatile caches, but financial ledgers require durability (`CryptoTrade`, `CryptoDepth`).
   - **Async Engine**: Uses `asyncpg` via SQLAlchemy's `AsyncSessionLocal` to prevent I/O blocking on database inserts.
5. **Data Presentation (GraphQL & REST)**
   - **Strawberry GraphQL**: Exposes a flexible API for quants to query specific time-windows of depth charts without over-fetching.

---

## 3. Programmer Handbook (Developer Guide)

### 3.1 Environment Setup
```bash
# 1. Ensure Python 3.11+ is installed
python -m venv venv
source venv/bin/activate

# 2. Install dependencies (relies on ferrox-py>=1.0.1)
pip install -r requirements.txt

# 3. Environment Variables (.env)
DATABASE_URL="postgresql+asyncpg://user:pass@localhost:5432/quant_db"
PASETO_SECRET_KEY="v4.local.YOUR_32_BYTE_SECRET_KEY_HERE"
```

### 3.2 Database Migrations & Models
Models are located in `modules/streaming/database.py`.
- **`CryptoTrade`**: Records execution prices, quantities, and side (BUY/SELL).
- **`CryptoDepth`**: Captures top-of-book Bid/Ask spreads.
Whenever you alter a model, ensure you run Alembic migrations (if integrated) or `Base.metadata.create_all(bind=engine)` is triggered safely.

### 3.3 Adding New Exchange Ingestors
To add a new exchange (e.g., Kraken):
1. Create `kraken_ingestor.py` mirroring `binance_ingestor.py`.
2. Implement the `async def stream_kraken()` function.
3. Register it in `main.py` inside the `lifespan` context manager using `asyncio.create_task()`.

### 3.4 Threat Engine Tuning
If the WAF generates false positives on complex GraphQL queries:
- Locate the `SentinelThreatEngineMiddleware` configuration.
- Adjust the **Shannon Entropy Threshold** (default is ~4.5 for alphanumeric, payload dependent).

---

## 4. User & DevOps Handbook (Operations)

### 4.1 Deployment Strategy
Because the ingestor maintains long-lived WebSockets, **Serverless (AWS Lambda) is NOT suitable**.
- **Recommended**: Kubernetes (EKS/GKE) or Docker Swarm on Bare-metal.
- **Scaling**: The Ingestor daemon should be run as a singleton (to avoid duplicate WebSocket streams), while the API layer (FastAPI) can scale horizontally behind an Ingress Controller.

### 4.2 Starting the Server
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```
*(Note: If running multiple workers, ensure your ingestor logic handles leader election, or extract the ingestor to a separate microservice).*

### 4.3 Monitoring & Metrics
Prometheus metrics are exposed at `/metrics` (or natively via middleware).
- Monitor `ferrox_threats_blocked_total` to track brute-force or injection attempts.
- Monitor `sqlalchemy_connection_pool` to ensure async DB connections are not exhausted during market volatility spikes.

---

## 5. Senior Engineering Decisions

1. **Why Async SQLAlchemy?** During high-volatility events, inserting 10,000 trades/sec synchronously would block the ASGI event loop, causing the application to drop WebSocket frames. `asyncpg` ensures the OS handles I/O multiplexing.
2. **Why PASETO over JWT?** In a zero-trust financial system, the cryptographic algorithm must be chosen by the server, not the header of the token. PASETO v4 local completely eliminates algorithm-downgrade attacks.
3. **Why Sentinel Threat Engine?** Traditional WAFs sit at the proxy layer (NGINX/Cloudflare). However, application-specific context (like Prompt Injections for ML models) requires a framework-integrated defense. Sentinel catches what edge WAFs miss.
