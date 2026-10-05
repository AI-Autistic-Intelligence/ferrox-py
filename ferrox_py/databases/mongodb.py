from typing import Any, Callable, Dict, List, Optional, Type, Set, cast, AsyncGenerator, Any, Callable, Dict, List, Optional, Type, Set, cast, AsyncGenerator
from ferrox_py.core.provider import injectable
from motor.motor_asyncio import AsyncIOMotorClient

@injectable()
class MongoService:
    def __init__(self, uri: str = "mongodb://localhost:27017") -> None:
        self.uri = uri
        self.client = AsyncIOMotorClient(self.uri)

    def get_database(self, name: str) -> Any:
        return self.client[name]

    def get_collection(self, db_name: str, coll_name: str) -> Any:
        return self.client[db_name][coll_name]
