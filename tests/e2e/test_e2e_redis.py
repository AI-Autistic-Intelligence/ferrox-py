import asyncio
import pytest
import pytest_asyncio
import redis.asyncio as redis

from ferrox_py.core.errors import FerroxError
from ferrox_py.security.distributed_locks import DistributedLockManager
from ferrox_py.security.rate_limiting import DistributedRateLimiter
from ferrox_py.resilience.circuit_breaker import (
    DistributedCircuitBreaker,
    CircuitBreakerOpenException,
)
from ferrox_py.concurrency.singleflight import SingleflightManager
from ferrox_py.architectures.sagas import (
    RedisSagaStateRepository,
    SagaOrchestrator,
    SagaStep,
)

# Connect to the real Redis spawned by docker-compose
REDIS_URL = "redis://localhost:6379"

@pytest_asyncio.fixture
async def real_redis():
    client = redis.from_url(REDIS_URL, decode_responses=True)
    # Ping to ensure it's up
    try:
        await client.ping()
    except Exception as e:
        pytest.skip(f"Redis is not available at {REDIS_URL}: {e}")
    
    # Clean DB before each test
    await client.flushdb()
    
    yield client
    
    await client.aclose()


@pytest.mark.asyncio
async def test_e2e_distributed_locks(real_redis):
    manager = DistributedLockManager(real_redis)

    async with manager.acquire("e2e_lock_key", ttl_ms=5000):
        with pytest.raises(FerroxError):
            async with manager.acquire("e2e_lock_key", timeout_ms=100):
                pass

    # Should be able to acquire again after release
    async with manager.acquire("e2e_lock_key", timeout_ms=100):
        assert True


@pytest.mark.asyncio
async def test_e2e_rate_limiter(real_redis):
    limiter = DistributedRateLimiter(real_redis)

    res1 = await limiter.check_and_consume("e2e_tenant", daily_limit=2)
    assert res1 is True

    res2 = await limiter.check_and_consume("e2e_tenant", daily_limit=2)
    assert res2 is True

    res3 = await limiter.check_and_consume("e2e_tenant", daily_limit=2)
    assert res3 is False


@pytest.mark.asyncio
async def test_e2e_circuit_breaker(real_redis):
    cb = DistributedCircuitBreaker(real_redis, max_failures=2, reset_timeout=1)

    async def failing_call():
        raise ValueError("e2e error")

    async def success_call():
        return "e2e ok"

    with pytest.raises(ValueError):
        await cb.call("e2e_tenant", "e2e_provider", failing_call)

    with pytest.raises(ValueError):
        await cb.call("e2e_tenant", "e2e_provider", failing_call)

    with pytest.raises(CircuitBreakerOpenException):
        await cb.call("e2e_tenant", "e2e_provider", success_call)

    await asyncio.sleep(1.1)

    res = await cb.call("e2e_tenant", "e2e_provider", success_call)
    assert res == "e2e ok"


@pytest.mark.asyncio
async def test_e2e_sagas(real_redis):
    repo = RedisSagaStateRepository(real_redis)
    orchestrator = SagaOrchestrator(repo)

    compensations = []

    async def step1(state):
        return "1"

    async def step1_comp(state):
        compensations.append("comp1")

    async def step2(state):
        raise ValueError("fail")

    steps = [
        SagaStep("step1", step1, step1_comp),
        SagaStep("step2", step2),
    ]

    with pytest.raises(FerroxError):
        await orchestrator.execute(steps)

    assert compensations == ["comp1"]
    
    # State should be updated in Redis (status = FAILED or COMPENSATED)
    # Check keys in Redis
    keys = await real_redis.keys("saga:*")
    assert len(keys) > 0


@pytest.mark.asyncio
async def test_e2e_singleflight():
    # Singleflight is typically in-memory but tested here as part of E2E validation
    manager = SingleflightManager()
    calls = 0

    async def my_task():
        nonlocal calls
        calls += 1
        await asyncio.sleep(0.1)
        return "e2e_result"

    results = await asyncio.gather(
        manager.do("e2e_key", my_task),
        manager.do("e2e_key", my_task),
        manager.do("e2e_key", my_task),
    )

    assert results == ["e2e_result", "e2e_result", "e2e_result"]
    assert calls == 1
