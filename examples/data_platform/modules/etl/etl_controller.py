import asyncio
from fastapi import APIRouter
from ferrox_py.pipelines.node import PipelineNode
from ferrox_py.pipelines.dag import DAG

class EtlController:
    def __init__(self, container):
        self.router = APIRouter(prefix="/etl", tags=["Data Pipelines (DAGs)"])
        self.container = container
        self.setup_routes()

    def setup_routes(self):
        @self.router.get("/trigger")
        async def trigger_pipeline():
            """
            Demonstrates Ferrox-Py's internal DAG engine for ETL workloads.
            """
            dag = DAG(name="Daily-Aggregations")
            
            # Create nodes (Steps in ETL)
            extract_users = PipelineNode("extract_users", lambda: {"users": 5000})
            extract_sales = PipelineNode("extract_sales", lambda: {"sales": 120000})
            
            async def transform_data():
                await asyncio.sleep(0.1) # simulate heavy transformation
                return {"transformed": True}
                
            transform = PipelineNode("transform", transform_data)
            transform.depends_on("extract_users", "extract_sales")
            
            async def load_to_warehouse():
                await asyncio.sleep(0.1) # simulate db insert
                return {"loaded": True}
                
            load = PipelineNode("load", load_to_warehouse)
            load.depends_on("transform")
            
            # Register in DAG
            dag.add_node(extract_users)
            dag.add_node(extract_sales)
            dag.add_node(transform)
            dag.add_node(load)
            
            # Execute the graph
            results = await dag.execute()
            
            return {
                "message": "ETL Pipeline Executed Successfully",
                "dag_name": dag.name,
                "execution_graph": results
            }
