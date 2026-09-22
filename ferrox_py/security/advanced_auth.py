from abc import ABC, abstractmethod
from typing import Dict
from ferrox_py.core.provider import injectable

class OAuth2Provider(ABC):
    @abstractmethod
    def get_auth_url(self) -> str:
        pass

    @abstractmethod
    async def exchange_code(self, code: str) -> Dict[str, str]:
        pass

@injectable()
class GoogleAuthProvider(OAuth2Provider):
    def __init__(self, client_id: str = "", client_secret: str = ""):
        self.client_id = client_id
        self.client_secret = client_secret

    def get_auth_url(self) -> str:
        return f"https://accounts.google.com/o/oauth2/v2/auth?client_id={self.client_id}"

    async def exchange_code(self, code: str) -> Dict[str, str]:
        # Exchange logic with httpx would go here
        return {"access_token": "mock_google_token", "email": "user@example.com"}
