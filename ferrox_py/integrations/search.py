from typing import Any, Callable, Dict, List, Optional, Type, Set, cast, AsyncGenerator, Any, Callable, Dict, List, Optional, Type, Set, cast, AsyncGenerator
from ferrox_py.core.provider import injectable

@injectable()
class SearchEngine:
    async def index_document(self, index_name: str, doc_id: str, document: Dict[Any, Any]) -> bool:
        return True

    async def search(self, index_name: str, query: str) -> List[Any]:
        return []
