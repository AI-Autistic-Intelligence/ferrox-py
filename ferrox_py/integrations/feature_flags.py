from typing import Any, Callable, Dict, List, Optional, Type, Set, cast, AsyncGenerator, Any, Callable, Dict, List, Optional, Type, Set, cast, AsyncGenerator
from ferrox_py.core.provider import injectable

@injectable()
class FeatureFlagService:
    def __init__(self) -> None:
        self.flags = {"new_ui": True, "beta_feature": False}

    async def is_enabled(self, flag_name: str) -> bool:
        return self.flags.get(flag_name, False)
