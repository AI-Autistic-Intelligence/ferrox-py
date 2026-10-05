import pytest
from ferrox_py.security.paseto import PasetoV4Engine
from ferrox_py.security.jwt import JwtService
from ferrox_py.security.rate_limiting import RateLimiter
from ferrox_py.security.distributed_locks import DistributedLockManager
from ferrox_py.core.errors import FerroxError

def test_paseto_encryption():
    engine = PasetoV4Engine("0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef")
    payload = {"user_id": 42, "role": "admin"}
    token = engine.encrypt(payload)
    assert token.startswith("v4.local.")
    
    decoded = engine.decrypt(token)
    assert decoded["user_id"] == 42
    assert decoded["role"] == "admin"

def test_jwt_engine():
    engine = JwtService("supersecret")
    payload = {"sub": "user123"}
    token = engine.sign(payload)
    
    assert isinstance(token, str)
    assert len(token.split(".")) == 3
    
    decoded = engine.verify(token)
    assert decoded["sub"] == "user123"
    
    with pytest.raises(Exception):
        engine.verify(token + "invalid")

@pytest.mark.asyncio
async def test_rate_limiter():
    limiter = RateLimiter()
    
    allowed1 = await limiter.is_allowed("ip_1", capacity=2, refill_rate=0)
    allowed2 = await limiter.is_allowed("ip_1", capacity=2, refill_rate=0)
    allowed3 = await limiter.is_allowed("ip_1", capacity=2, refill_rate=0)
    
    assert allowed1 is True
    assert allowed2 is True
    assert allowed3 is False  # Limit exceeded

@pytest.mark.asyncio
async def test_distributed_lock():
    lock_manager = DistributedLockManager()
    
    # Should acquire lock
    async with lock_manager.acquire("resource1", timeout_ms=5000):
        # Inside lock
        # Trying to acquire same lock without releasing will raise FerroxError if timeout is very small
        with pytest.raises(FerroxError):
            async with lock_manager.acquire("resource1", timeout_ms=100):
                pass
    
    # After releasing, it should be acquirable again
    async with lock_manager.acquire("resource1", timeout_ms=5000):
        pass
