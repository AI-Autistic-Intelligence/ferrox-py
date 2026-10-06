
from ferrox_py.core.provider import injectable


@injectable()
class HealthIndicator:
    def __init__(self) -> None:
        pass

    async def check_health(self) -> dict[str, str]:
        return {
            "status": "up",
            "database": "connected",
            "redis": "connected"
        }
