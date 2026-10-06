from abc import ABC, abstractmethod

from fastapi import Request


class Guard(ABC):
    @abstractmethod
    async def can_activate(self, request: Request) -> bool:
        pass

class MandatoryComplianceGuard(Guard):
    async def can_activate(self, request: Request) -> bool:
        # Example check for mandatory compliance headers
        if not request.headers.get("X-Compliance-Check"):
            return False
        return True
