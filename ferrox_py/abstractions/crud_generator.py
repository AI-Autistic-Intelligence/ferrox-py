from typing import Any

from fastapi import APIRouter


def generate_crud_controller(entity: type[Any], service: type[Any], prefix: str) -> Any:
    """
    Generates a standard FastAPI router with CRUD operations for an entity.
    """
    router = APIRouter(prefix=prefix, tags=[entity.__name__])

    @router.get("/")
    async def get_all() -> Any:
        return {"action": "get_all", "entity": entity.__name__}
        
    @router.get("/{id}")
    async def get_one(id: str) -> Any:
        return {"action": "get_one", "id": id, "entity": entity.__name__}

    @router.post("/")
    async def create(data: dict[Any, Any]) -> Any:
        return {"action": "create", "data": data, "entity": entity.__name__}
        
    @router.put("/{id}")
    async def update(id: str, data: dict[Any, Any]) -> Any:
        return {"action": "update", "id": id, "data": data, "entity": entity.__name__}
        
    @router.delete("/{id}")
    async def delete(id: str) -> Any:
        return {"action": "delete", "id": id, "entity": entity.__name__}

    return router
