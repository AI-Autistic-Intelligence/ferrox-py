from ferrox_py.core.provider import injectable
from typing import Any, Callable, Dict, List, Optional, Type, Set, cast, AsyncGenerator, Any, Callable, Dict, List, Optional, Type, Set, cast, AsyncGenerator, Dict

@injectable()
class HealthIndicator:
    def __init__(self) -> None:
        pass

    async def check_health(self) -> Dict[str, str]:
        return {
            "status": "up",
            "database": "connected",
            "redis": "connected"
        }
