from ferrox_py.core.provider import injectable
from typing import Dict

@injectable()
class HealthIndicator:
    def __init__(self):
        pass

    async def check_health(self) -> Dict[str, str]:
        return {
            "status": "up",
            "database": "connected",
            "redis": "connected"
        }
