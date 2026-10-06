from abc import ABC, abstractmethod

from pydantic import BaseModel

from ferrox_py.core.errors import FerroxError
from ferrox_py.core.provider import injectable


class MailException(FerroxError):
    def __init__(self, message: str):
        super().__init__(message=message, status_code=500)

class MailAttachment(BaseModel):
    filename: str
    content: bytes
    mime_type: str

class MailMessage(BaseModel):
    to: list[str]
    subject: str
    template_id: str | None = None
    body_html: str | None = None
    attachments: list[MailAttachment] | None = None

class MailerService(ABC):
    @abstractmethod
    async def send_mail(self, message: MailMessage) -> bool:
        pass

@injectable()
class DummyMailerService(MailerService):
    async def send_mail(self, message: MailMessage) -> bool:
        # Placeholder for actual implementation (e.g. SendGrid, AWS SES)
        print(f"Sending email to {message.to}...")
        return True
