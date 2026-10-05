from typing import Any, Callable, Dict, List, Optional, Type, Set, cast, AsyncGenerator, Any, Callable, Dict, List, Optional, Type, Set, cast, AsyncGenerator
import json
import pyseto
from pyseto import Key

class PasetoV4Engine:
    def __init__(self, symmetric_key_hex: str) -> None:
        # Using PASETO v4 local
        self.key = Key.new(version=4, purpose="local", key=bytes.fromhex(symmetric_key_hex))
        
    def encrypt(self, payload: Dict[Any, Any]) -> str:
        payload_bytes = json.dumps(payload).encode('utf-8')
        token = pyseto.encode(self.key, payload_bytes)
        return token.decode("utf-8")
        
    def decrypt(self, token: str) -> Dict[Any, Any]:
        decoded = pyseto.decode(self.key, token)
        return json.loads(decoded.payload.decode('utf-8'))
