from ferrox_py.core.provider import injectable

@injectable()
class SearchEngine:
    async def index_document(self, index_name: str, doc_id: str, document: dict) -> bool:
        return True

    async def search(self, index_name: str, query: str) -> list:
        return []
