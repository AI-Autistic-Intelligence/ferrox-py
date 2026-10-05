from typing import Any, Callable, Dict, List, Optional, Type, Set, cast, AsyncGenerator, Any, Callable, Dict, List, Optional, Type, Set, cast, AsyncGenerator
from ferrox_py.core.provider import injectable

@injectable()
class I18nService:
    def __init__(self) -> None:
        self.default_locale = "en"

    def translate(self, key: str, locale: Optional[Optional[str]] = None) -> str:
        loc = locale or self.default_locale
        # Dummy translation lookup
        return f"[{loc}] {key}"
