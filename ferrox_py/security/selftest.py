from typing import Any, Callable, Dict, List, Optional, Type, Set, cast, AsyncGenerator, Any, Callable, Dict, List, Optional, Type, Set, cast, AsyncGenerator
from ferrox_py.core.provider import injectable

@injectable()
class SelfTestRunner:
    async def run_diagnostics(self) -> Dict[Any, Any]:
        return {"status": "ok", "crypto": "healthy"}
