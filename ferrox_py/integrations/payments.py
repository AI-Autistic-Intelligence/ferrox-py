from abc import ABC, abstractmethod

from pydantic import BaseModel

from ferrox_py.core.errors import FerroxError
from ferrox_py.core.provider import injectable


class PaymentException(FerroxError):
    def __init__(self, message: str):
        super().__init__(message=message, status_code=402) # 402 Payment Required

class PaymentItem(BaseModel):
    name: str
    amount_cents: int
    quantity: int

class CheckoutRequest(BaseModel):
    items: list[PaymentItem]
    currency: str = "USD"
    success_url: str
    cancel_url: str

class PaymentGateway(ABC):
    @abstractmethod
    async def create_checkout_session(self, request: CheckoutRequest) -> str:
        """Returns a checkout URL or session ID."""

@injectable()
class DummyPaymentGateway(PaymentGateway):
    async def create_checkout_session(self, request: CheckoutRequest) -> str:
        return "checkout_session_id_123"
