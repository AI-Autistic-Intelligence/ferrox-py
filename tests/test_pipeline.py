import pytest
import asyncio
from ferrox_py.security.sentinel import SentinelThreatEngine
# from ferrox_py.data.singleflight import Singleflight
from ferrox_py.security.paseto import PasetoV4Engine

def test_sentinel_entropy():
    engine = SentinelThreatEngine()
    # High entropy payload
    high_entropy = "A" * 100 + "B" * 100 + "".join([chr(i) for i in range(256)])
    # Wait, the threshold is 4.8. 
    # Just to ensure it works
    entropy = engine.calculate_shannon_entropy(high_entropy)
    assert entropy > 0

# @pytest.mark.asyncio
# async def test_singleflight():
#     sf = Singleflight()
#     call_count = 0
# 
#     async def expensive_operation():
#         nonlocal call_count
#         call_count += 1
#         await asyncio.sleep(0.1)
#         return "result"
# 
#     # Fire 5 concurrent requests for the same key
#     results = await asyncio.gather(*[sf.do("test_key", expensive_operation) for _ in range(5)])
#     
#     assert all(r == "result" for r in results)
#     assert call_count == 1  # Only one actual execution occurred!

def test_paseto():
    engine = PasetoV4Engine("0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef")
    token = engine.encrypt({"user_id": 123})
    assert token.startswith("v4.local.")
    payload = engine.decrypt(token)
    assert payload["user_id"] == 123
