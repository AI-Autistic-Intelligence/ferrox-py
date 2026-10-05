from typing import Any, Callable, Dict, List, Optional, Type, Set, cast, AsyncGenerator, Any, Callable, Dict, List, Optional, Type, Set, cast, AsyncGenerator
import json
import base64
import hmac
import hashlib
import time
from ferrox_py.core.provider import injectable
from ferrox_py.core.errors import FerroxError

@injectable()
class JwtService:
    def __init__(self, secret: str = "ferrox_default_secret_key") -> None:
        self.secret = secret.encode()

    def _encode_b64(self, payload: Dict[Any, Any]) -> str:
        json_payload = json.dumps(payload, separators=(',', ':')).encode()
        return base64.urlsafe_b64encode(json_payload).decode().rstrip("=")

    def sign(self, payload: Dict[Any, Any], expiration_seconds: int = 3600) -> str:
        header = {"alg": "HS256", "typ": "JWT"}
        if "exp" not in payload:
            payload["exp"] = int(time.time()) + expiration_seconds
            
        b64_header = self._encode_b64(header)
        b64_payload = self._encode_b64(payload)
        
        signature = hmac.new(self.secret, f"{b64_header}.{b64_payload}".encode(), hashlib.sha256).digest()
        b64_signature = base64.urlsafe_b64encode(signature).decode().rstrip("=")
        
        return f"{b64_header}.{b64_payload}.{b64_signature}"

    def verify(self, token: str) -> Dict[Any, Any]:
        parts = token.split(".")
        if len(parts) != 3:
            raise FerroxError(message="Invalid JWT format", status_code=401)
            
        b64_header, b64_payload, b64_signature = parts
        
        expected_sig = hmac.new(self.secret, f"{b64_header}.{b64_payload}".encode(), hashlib.sha256).digest()
        expected_b64_sig = base64.urlsafe_b64encode(expected_sig).decode().rstrip("=")
        
        if not hmac.compare_digest(b64_signature, expected_b64_sig):
            raise FerroxError(message="Invalid JWT signature", status_code=401)
            
        # Add padding back to decode payload
        padded_payload = b64_payload + "=" * ((4 - len(b64_payload) % 4) % 4)
        payload = json.loads(base64.urlsafe_b64decode(padded_payload))
        
        if "exp" in payload and int(time.time()) > payload["exp"]:
            raise FerroxError(message="JWT token expired", status_code=401)
            
        return payload
