# Ferrox-Py Quantitative Data Platform - The Definitive Handbook

## 1. Executive Summary & Senior Engineering Vision

This document serves as the absolute source of truth for the **Quantitative Data Platform**, the official Ferrox-Py reference architecture. 

As a Senior Engineer, I designed this platform to process High-Frequency Trading (HFT) and Quantitative Market Data. In this domain, a missed tick or a garbage collection pause translates directly to financial loss. This system represents the pinnacle of Python async engineering, proving that when Python is intimately coupled with the Linux kernel's event loop (`epoll`), it can rival compiled languages in I/O throughput.

This handbook details the complete lifecycle of the platform: from the hardware interrupts to the userland Python AST, down to the persistence layers.

---

## 2. The Domain Problem

Financial exchanges (like Binance, Kraken, and CME) blast millions of JSON or binary payloads via WebSockets. We must:
1. Maintain unyielding, non-blocking TCP connections.
2. Parse variable-length streams instantaneously.
3. Validate and sanitize payloads against malformed data and malicious injections (zero-trust).
4. Persist data with strict ACID guarantees (preventing ledger corruption).
5. Expose historical and real-time aggregations via GraphQL and REST without blocking the ingestor.

---

## 3. Low-Level Architecture & OS-Kernel Interactions

We do not view Python as a void; we view it as an orchestrator of OS syscalls.

### 3.1 The Epoll Bridge & Socket Tuning
Python's Global Interpreter Lock (GIL) is bypassed by moving the I/O multiplexing into C. We use `uvloop` (a Cython wrapper for `libuv`) which interfaces directly with Linux `epoll` or macOS `kqueue`.
- **TCP_NODELAY**: Sockets are configured to disable Nagle's algorithm. In trading, waiting to buffer 1500 bytes before sending a packet causes unacceptable latency. Packets are flushed to the NIC immediately.
- **SO_REUSEPORT**: We allow multiple Python worker processes to bind to the same inbound API port (8000). The Linux kernel distributes incoming TCP SYNs across the processes, maximizing multi-core CPU utilization.

### 3.2 Thread Starvation & Context Switching
Because the GIL exists, CPU-bound tasks (like heavy JSON deserialization or cryptographic signing) will starve the event loop, causing dropped WebSocket frames. We strictly offload these tasks to Rust-based libraries (`orjson`) or C-extensions, allowing the Python thread to hit `epoll_wait` as frequently as possible.

---

## 4. Application Layer & Framework Internals

### 4.1 FastAPI / Starlette Foundation
The platform uses the ASGI standard. The outer routing boundary is handled by FastAPI for automatic OpenAPI generation and Pydantic schema validation.
- **Background Daemons**: The WebSocket ingestors run as background Tasks, initialized via Starlette's `@asynccontextmanager` lifecycle. They are isolated from the HTTP request/response cycle.

### 4.2 GraphQL Integration
We utilize **Strawberry GraphQL** for data presentation. Quants do not want to pull 10GB of REST data to analyze a 1-minute window. GraphQL allows strict, graph-based querying of order books and trade ledgers.

---

## 5. Security Model: Zero-Trust & Cryptography

### 5.1 Sentinel Threat Engine (WAF)
Regex-based Web Application Firewalls are fundamentally flawed. A crafted payload can trigger Catastrophic Backtracking (`O(2^n)` complexity), bringing down the server via ReDoS.
- **Shannon Entropy Analysis**: Our `SentinelThreatEngineMiddleware` calculates the informational entropy of the incoming byte stream: `H(X) = -Σ P(x) * log2 P(x)`. High entropy (e.g., > 4.8 bits/byte) immediately flags the payload as potentially obfuscated shellcode, SQLi, or Prompt Injection. This mathematical analysis runs in linear `O(N)` time.

### 5.2 PASETO v4 over JWT
JWT allows "Algorithm Confusion" (e.g., switching RSA to HMAC) because the token dictates the algorithm. 
- **PASETO v4 Local**: We enforce `XChaCha20-Poly1305` authenticated encryption. The algorithm is structurally bound to the protocol version. Verification relies on constant-time C functions to prevent side-channel timing attacks.

---

## 6. Persistence & ACID Strategy

### 6.1 PostgreSQL & asyncpg
We explicitly abandoned Redis streams for this ledger to guarantee ACID durability.
- **Binary Protocol Mapping**: We use `asyncpg`. It speaks the PostgreSQL frontend/backend protocol natively over TCP, bypassing the blocking `libpq` C-library. It maps binary IEEE 754 floats from the DB directly to Python types, bypassing UTF-8 string parsing overhead.

### 6.2 Write-Ahead Logging (WAL) Tuning
During extreme volatility, inserting rows one by one kills performance due to disk fsync limits. We rely on SQLAlchemy's `AsyncSessionLocal` to batch inserts. The OS kernel's page cache holds the dirty pages, while Postgres `wal_writer_delay` groups WAL flushes, achieving sequential disk write speeds.

---

## 7. Programmer's Guide (Developer Workflow)

### 7.1 Environment Setup
```bash
# 1. Create a pristine virtual environment
python3.11 -m venv venv
source venv/bin/activate

# 2. Install dependencies (Requires ferrox-py>=1.0.1)
# Use CFLAGS to optimize C-extensions for your CPU architecture
CFLAGS="-O3 -march=native" pip install -r requirements.txt

# 3. Environment Configuration (.env)
DATABASE_URL="postgresql+asyncpg://ferrox:password@localhost:5432/quant_db"
PASETO_SECRET_KEY="v4.local.YOUR_32_BYTE_SECRET_KEY_HERE"
```

### 7.2 Creating a New Ingestor (e.g., Coinbase)
1. Navigate to `modules/streaming/`.
2. Create `coinbase_ingestor.py`.
3. Implement `async def stream_coinbase()` using the `websockets` library.
4. Implement exponential backoff in a `while True:` loop to handle exchange disconnects.
5. In `main.py`, add `asyncio.create_task(stream_coinbase())` to the `lifespan` context manager.

### 7.3 Database Migrations (Alembic)
Whenever `CryptoTrade` or `CryptoDepth` models are altered in `database.py`:
```bash
alembic revision --autogenerate -m "Added trade volume column"
alembic upgrade head
```

---

## 8. User & DevOps Handbook (Operations)

### 8.1 OS & Sysctl Tuning for HFT
Before deploying, the Linux kernel must be tuned:
```bash
# Prevent ephemeral port exhaustion
sysctl -w net.ipv4.tcp_tw_reuse=1
# Increase max connection backlog
sysctl -w net.core.somaxconn=65535
# Tune TCP read/write memory buffers
sysctl -w net.ipv4.tcp_rmem="4096 87380 16777216"
sysctl -w net.ipv4.tcp_wmem="4096 65536 16777216"
```

### 8.2 Deployment: Docker & Uvicorn
Serverless (AWS Lambda) is unacceptable due to long-lived WebSockets. Deploy on Kubernetes or Docker Swarm.
```bash
# Run with Uvicorn utilizing uvloop
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4 --loop uvloop --http httptools
```
*Warning: Running 4 workers spawns 4 background ingestors. Ensure your ingestors have a leader-election mechanism (e.g., Redis Lock) or extract the ingestors to a separate singleton microservice.*

---

## 9. Observability & Telemetry

### 9.1 Prometheus Metrics
The platform exposes `/metrics` for Prometheus scraping.
- `ferrox_threats_blocked_total`: Counter for WAF interventions.
- `ferrox_ingestion_latency_ms`: Histogram of time from WebSocket read to Postgres commit.
- `sqlalchemy_connection_pool_active`: Gauge for DB saturation.

### 9.2 Log Redaction
Use `structlog` to output JSON lines for ELK/Datadog. Ensure `PASETO` tokens and passwords are redacted via custom processors before hitting `stdout`.
