import asyncio

import pytest

from ferrox_py.resilience.circuit_breaker import (
    CircuitBreaker,
    CircuitBreakerOpenException,
)


@pytest.mark.asyncio
async def test_circuit_breaker():
    breaker = CircuitBreaker(max_failures=2, reset_timeout=1)
    call_count = 0
    
    async def unstable_service(fail: bool):
        nonlocal call_count
        call_count += 1
        if fail:
            raise ValueError("Service Failed")
        return "Success"
        
    # 1. Success call
    res = await breaker.call(unstable_service, False)
    assert res == "Success"
    assert call_count == 1
    
    # 2. Fail 1
    with pytest.raises(ValueError):
        await breaker.call(unstable_service, True)
        
    # 3. Fail 2 (Threshold reached, breaker opens)
    with pytest.raises(ValueError):
        await breaker.call(unstable_service, True)
        
    # 4. Breaker is open, should raise exception without calling service
    with pytest.raises(CircuitBreakerOpenException):
        await breaker.call(unstable_service, False)
    
    assert call_count == 3  # Did not increment!
    
    # 5. Wait for recovery
    await asyncio.sleep(1.1)
    
    # 6. Half-open, next call succeeds and closes breaker
    res = await breaker.call(unstable_service, False)
    assert res == "Success"
    assert call_count == 4
