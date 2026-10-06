from typing import Any

from motor.motor_asyncio import AsyncIOMotorClient

from ferrox_py.core.provider import injectable


@injectable()
class MongoService:
    def __init__(self, uri: str = "mongodb://localhost:27017") -> None:
        self.uri = uri
        self.client = AsyncIOMotorClient(self.uri)  # type: ignore

    def get_database(self, name: str) -> Any:
        return self.client[name]

    def get_collection(self, db_name: str, coll_name: str) -> Any:
        return self.client[db_name][coll_name]
