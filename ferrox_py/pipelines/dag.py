import asyncio
from typing import Any, Callable, Dict, List, Optional, Type, Set, cast, AsyncGenerator, Any, Callable, Dict, List, Optional, Type, Set, cast, AsyncGenerator, Dict, Any
from .node import PipelineNode
from structlog import get_logger

logger = get_logger()

class DAG:
    """
    Directed Acyclic Graph Orchestrator for Ferrox-Py Data Platforms.
    Executes ETL nodes concurrently based on their dependency graph.
    """
    def __init__(self, name: str) -> None:
        self.name = name
        self.nodes: Dict[str, PipelineNode] = {}
        
    def add_node(self, node: PipelineNode) -> Any:
        if node.node_id in self.nodes:
            raise ValueError(f"Node {node.node_id} already exists in DAG {self.name}")
        self.nodes[node.node_id] = node
        
    async def execute(self) -> Dict[str, Any]:
        """
        Runs the DAG, respecting dependencies.
        Nodes with no pending dependencies are executed concurrently.
        """
        logger.info("dag_started", dag=self.name)
        results = {}
        pending = set(self.nodes.keys())
        completed: Set[str] = set()
        
        # Async tasks mapping
        tasks: Dict[str, asyncio.Task] = {}
        
        while pending:
            # Find nodes whose dependencies are all completed
            ready = {
                n for n in pending 
                if self.nodes[n].dependencies.issubset(completed) and n not in tasks
            }
            
            if not ready and not tasks:
                # Circular dependency or missing node
                raise RuntimeError(f"DAG Execution Stalled. Check dependencies. Pending: {pending}")
                
            # Schedule ready nodes
            for node_id in ready:
                node = self.nodes[node_id]
                logger.info("node_started", dag=self.name, node=node_id)
                # Pass results of dependencies to the node if needed (simple injection)
                # In a real heavy ETL, you'd pass a context object. Here we just run it.
                tasks[node_id] = asyncio.create_task(node.execute())
                
            # Wait for at least one task to complete
            done, _ = await asyncio.wait(tasks.values(), return_when=asyncio.FIRST_COMPLETED)
            
            for task in done:
                # Find which node this task belongs to
                node_id = next(nid for nid, t in tasks.items() if t == task)
                try:
                    result = task.result()
                    results[node_id] = result
                    completed.add(node_id)
                    pending.remove(node_id)
                    del tasks[node_id]
                    logger.info("node_completed", dag=self.name, node=node_id)
                except Exception as e:
                    logger.error("node_failed", dag=self.name, node=node_id, error=str(e))
                    raise RuntimeError(f"DAG Execution Failed at node {node_id}") from e
                    
        logger.info("dag_completed", dag=self.name)
        return results
