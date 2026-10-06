import asyncio
from collections.abc import Callable
from typing import Any


class PipelineNode:
    """
    A single unit of work in a Directed Acyclic Graph (DAG) for ETL pipelines.
    """
    def __init__(self, node_id: str, action: Callable[..., Any]) -> None:
        self.node_id = node_id
        self.action = action
        self.dependencies: set[str] = set()
        self.result: Any | None = None
        self.status: str = "PENDING"  # PENDING, RUNNING, SUCCESS, FAILED
        
    def depends_on(self, *node_ids: str) -> Any:
        for nid in node_ids:
            self.dependencies.add(nid)
            
    async def execute(self, *args, **kwargs) -> Any:  # type: ignore
        self.status = "RUNNING"
        try:
            if asyncio.iscoroutinefunction(self.action):
                self.result = await self.action(*args, **kwargs)
            else:
                self.result = self.action(*args, **kwargs)
            self.status = "SUCCESS"
            return self.result
        except Exception as e:
            self.status = "FAILED"
            raise e
