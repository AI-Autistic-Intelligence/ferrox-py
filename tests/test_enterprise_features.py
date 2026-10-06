import asyncio

import pytest
import pytest_asyncio
from fakeredis.aioredis import FakeRedis

from ferrox_py.architectures.sagas import (
    RedisSagaStateRepository,
    SagaOrchestrator,
    SagaStep,
)
from ferrox_py.concurrency.singleflight import SingleflightManager
from ferrox_py.core.errors import FerroxError
from ferrox_py.resilience.circuit_breaker import (
    CircuitBreakerOpenException,
    DistributedCircuitBreaker,
)
from ferrox_py.security.distributed_locks import DistributedLockManager
from ferrox_py.security.rate_limiting import DistributedRateLimiter
from ferrox_py_utils.connectors.integration_connector import (
    IntegrationConnector,
    connector_policy,
    resilient_sync,
)


@pytest_asyncio.fixture
async def redis():
    client = FakeRedis()
    yield client
    await client.aclose()


@pytest.mark.asyncio
async def test_singleflight():
    manager = SingleflightManager()
    calls = 0

    async def my_task():
        nonlocal calls
        calls += 1
        await asyncio.sleep(0.1)
        return "result"

    results = await asyncio.gather(
        manager.do("key1", my_task),
        manager.do("key1", my_task),
        manager.do("key1", my_task),
    )

    assert results == ["result", "result", "result"]
    assert calls == 1


@pytest.mark.asyncio
async def test_distributed_locks(redis):
    manager = DistributedLockManager(redis)

    async with manager.acquire("lock_key", ttl_ms=5000):
        with pytest.raises(FerroxError):
            async with manager.acquire("lock_key", timeout_ms=100):
                pass

    async with manager.acquire("lock_key", timeout_ms=100):
        assert True


@pytest.mark.asyncio
async def test_rate_limiter(redis):
    limiter = DistributedRateLimiter(redis)

    res = await limiter.check_and_consume("tenant1", daily_limit=2)
    assert res is True
    res = await limiter.check_and_consume("tenant1", daily_limit=2)
    assert res is True
    res = await limiter.check_and_consume("tenant1", daily_limit=2)
    assert res is False


@pytest.mark.asyncio
async def test_circuit_breaker(redis):
    cb = DistributedCircuitBreaker(redis, max_failures=2, reset_timeout=1)

    async def failing_call():
        raise ValueError("error")

    async def success_call():
        return "ok"

    with pytest.raises(ValueError):
        await cb.call("t1", "prov1", failing_call)

    with pytest.raises(ValueError):
        await cb.call("t1", "prov1", failing_call)

    with pytest.raises(CircuitBreakerOpenException):
        await cb.call("t1", "prov1", success_call)

    await asyncio.sleep(1.1)

    res = await cb.call("t1", "prov1", success_call)
    assert res == "ok"


@pytest.mark.asyncio
async def test_sagas(redis):
    repo = RedisSagaStateRepository(redis)
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


@pytest.mark.asyncio
async def test_integration_connector(redis):
    lock_manager = DistributedLockManager(redis)
    rate_limiter = DistributedRateLimiter(redis)
    circuit_breaker = DistributedCircuitBreaker(redis, max_failures=2, reset_timeout=1)
    singleflight_manager = SingleflightManager()

    class MockConnector(IntegrationConnector):
        def __init__(self):
            super().__init__(lock_manager, rate_limiter, circuit_breaker, singleflight_manager)
            self.calls = 0

        @resilient_sync(singleflight=True, retry=3, backoff="constant")
        @connector_policy(provider="shopify", max_concurrency=1, daily_quota=10)
        async def fetch_data(self, tenant_id: str, should_fail: bool = False):
            self.calls += 1
            if should_fail:
                raise ValueError("API error")
            await asyncio.sleep(0.1)
            return "data"

    connector = MockConnector()

    # Test singleflight and concurrency
    results = await asyncio.gather(
        connector.fetch_data("tenant1"),
        connector.fetch_data("tenant1"),
        connector.fetch_data("tenant1"),
    )
    assert results == ["data", "data", "data"]
    # Due to singleflight, only 1 actual execution should happen
    assert connector.calls == 1

    # Test rate limiting (quota is 10)
    for _ in range(9):
        await connector.fetch_data("tenant1")
