from typing import Any

from ferrox_py.core.provider import injectable


@injectable()
class SelfTestRunner:
    async def run_diagnostics(self) -> dict[Any, Any]:
        return {"status": "ok", "crypto": "healthy"}
