import hmac
import hashlib
import time

class MTDEngine:
    """Moving Target Defense: Ephemeral HMAC Route Tokens."""
    def __init__(self, secret: bytes, validity_window: int = 30):
        self.secret = secret
        self.validity_window = validity_window

    def generate_token(self, path: str) -> str:
        current_window = int(time.time()) // self.validity_window
        msg = f"{path}:{current_window}".encode("utf-8")
        return hmac.new(self.secret, msg, hashlib.sha256).hexdigest()

    def validate_token(self, path: str, token: str) -> bool:
        expected = self.generate_token(path)
        return hmac.compare_digest(expected, token)
