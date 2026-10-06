from typing import Any

from ferrox_py.core.provider import injectable


@injectable()
class SearchEngine:
    async def index_document(self, index_name: str, doc_id: str, document: dict[Any, Any]) -> bool:
        return True

    async def search(self, index_name: str, query: str) -> list[Any]:
        return []
