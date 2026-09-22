from abc import ABC, abstractmethod
from typing import List, Optional
from pydantic import BaseModel
from ferrox_py.core.provider import injectable
from ferrox_py.core.errors import FerroxError

class MailException(FerroxError):
    def __init__(self, message: str):
        super().__init__(message=message, status_code=500)

class MailAttachment(BaseModel):
    filename: str
    content: bytes
    mime_type: str

class MailMessage(BaseModel):
    to: List[str]
    subject: str
    template_id: Optional[str] = None
    body_html: Optional[str] = None
    attachments: Optional[List[MailAttachment]] = None

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
