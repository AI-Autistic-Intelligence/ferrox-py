from fastapi import Request

from ferrox_py.core.provider import injectable


@injectable()
class WebhookValidator:
    def __init__(self, secret: str = "webhook_secret"):
        self.secret = secret

    async def validate_signature(self, request: Request) -> bool:
        # Example validation logic (HMAC SHA256)
        signature = request.headers.get("X-Webhook-Signature")
        return signature is not None
