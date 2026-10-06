# Distributed Rate Limiting

## 1. Overview (What does this do?)
The `DistributedRateLimiter` enforces strict API quotas and usage throttling across an entire server cluster. Instead of tracking requests per-second in local memory, it uses Redis to globally synchronize how many times a specific user, tenant, or IP address has accessed a resource, denying access gracefully when their quota is exceeded.

## 2. Philosophy (Why does it exist?)
Unrestricted endpoints are vulnerable to DoS (Denial of Service) attacks, aggressive bot scraping, and accidental internal infinite loops. The philosophy is Active Defense: an enterprise application must natively defend its resources and external API quotas from abuse. Distributing this logic guarantees that routing algorithms in load balancers do not bypass the rate limit by sending requests to different nodes.

## 3. Target Audience (Who is it for?)
This component is essential for SaaS platforms offering tiered subscriptions (e.g., "Free users get 100 API calls/day, Pro users get 10,000"), and for security engineers defending public-facing GraphQL and REST endpoints against brute force attacks.

## 4. Architecture (How does it work?)
The `DistributedRateLimiter` employs a high-performance Redis Lua script (often implementing a Token Bucket or sliding window algorithm) to evaluate and decrement quotas atomically.
- **check_and_consume**: An atomic operation that verifies if a key has remaining quota and instantly consumes one token.
- Because it is executed directly on the Redis engine via Lua, it absolutely prevents race conditions where a sudden burst of parallel requests might all pass the "check" phase before the quota is consumed.

## 5. Installation / Setup
The rate limiter is part of the core `ferrox-py` security suite. A Redis backend is required to maintain the global token buckets.

```bash
pip install ferrox-py
```
You can inject the rate limiter directly into Layer 2 of the 7-Layer Onion Pipeline.

## 6. Quickstart (Usage)
```python
from ferrox_py.security.rate_limiting import DistributedRateLimiter
import redis.asyncio as redis

async def check_api_quota(tenant_id: str):
    client = redis.from_url("redis://localhost")
    limiter = DistributedRateLimiter(client)
    
    # Restrict to 1000 requests per day per tenant
    allowed = await limiter.check_and_consume(tenant_id, daily_limit=1000)
    
    if not allowed:
        raise Exception("HTTP 429: Too Many Requests - Daily Quota Exceeded")
        
    print("Request allowed!")
```

## 7. Ecosystem Integration
The Rate Limiter operates directly within the **Sentinel Threat Engine** (Layer 3 of the pipeline) to globally throttle suspicious IP addresses. It also integrates seamlessly with the **Connectors** (via `ferrox-py-utils`), ensuring that outgoing requests to sensitive third-party APIs (like Shopify or AWS) never exceed the vendor's hard rate limits, thus preventing account bans.
