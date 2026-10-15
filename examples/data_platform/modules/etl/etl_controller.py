import asyncio
import time
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Query, status
from pydantic import BaseModel, Field

from ferrox_py.pipelines.dag import DAG
from ferrox_py.pipelines.node import PipelineNode
from ..persistence import get_repository


class PipelineExecutionResponse(BaseModel):
    message: str
    dag_name: str
    duration_ms: float
    execution_graph: Dict[str, Any]


class EtlController:
    def __init__(self, container):
        self.router = APIRouter(prefix="/etl", tags=["Data Pipelines (DAGs)"])
        self.container = container
        self.repo = get_repository()
        self.setup_routes()

    def setup_routes(self):
        @self.router.get(
            "/trigger",
            response_model=Dict[str, Any],
            summary="Execute Daily Aggregations DAG",
            description="Executes a 4-node Directed Acyclic Graph (DAG) for parallel extraction, transformation, and warehouse loading.",
        )
        async def trigger_pipeline():
            start_time = time.perf_counter()
            dag = DAG(name="Daily-Aggregations")

            # Create nodes (Steps in ETL)
            extract_users = PipelineNode("extract_users", lambda: {"active_users": 5240, "new_users": 180})
            extract_sales = PipelineNode("extract_sales", lambda: {"gross_sales_usd": 128450.0, "transactions": 1420})

            async def transform_data():
                await asyncio.sleep(0.05)  # simulate parallelized async processing
                return {"aggregated": True, "currency": "USD", "conversion_rate": 0.27}

            transform = PipelineNode("transform", transform_data)
            transform.depends_on("extract_users", "extract_sales")

            async def load_to_warehouse():
                await asyncio.sleep(0.05)  # simulate warehouse insertion
                return {"loaded": True, "partition": "2026-10-15"}

            load = PipelineNode("load", load_to_warehouse)
            load.depends_on("transform")

            # Register in DAG
            dag.add_node(extract_users)
            dag.add_node(extract_sales)
            dag.add_node(transform)
            dag.add_node(load)

            # Execute the graph
            results = await dag.execute()
            duration_ms = round((time.perf_counter() - start_time) * 1000, 2)

            # Persist execution trace
            await self.repo.record_pipeline_run(
                dag_name=dag.name,
                status="completed",
                duration_ms=duration_ms,
                results=results,
            )

            return {
                "message": "ETL Pipeline Executed Successfully",
                "dag_name": dag.name,
                "duration_ms": duration_ms,
                "execution_graph": results,
            }

        @self.router.get(
            "/runs",
            response_model=Dict[str, Any],
            summary="Get Pipeline Run History",
            description="Retrieves execution audit records for all DAG workflows.",
        )
        async def get_pipeline_runs(
            limit: int = Query(20, ge=1, le=100, description="Maximum number of DAG runs to return"),
        ):
            runs = await self.repo.list_pipeline_runs(limit=limit)
            return {"total": len(runs), "runs": runs}
