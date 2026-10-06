from typing import Any

from ferrox_py_utils.pipelines.orchestrator import PipelineOrchestrator, PipelineStep
from ferrox_py_utils.schemas.registry import SchemaRegistry

from ferrox_py.core.provider import injectable


@injectable()
class IngestionService:
    def __init__(self):
        self.orchestrator = PipelineOrchestrator()
        self.registry = SchemaRegistry()
        
        # Register dynamic schema for weather metrics
        self.registry.register_schema("WeatherMetric", {
            "city": (str, ...),
            "temperature": (float, ...),
            "humidity": (int, ...)
        })

    async def _extract(self, payload: Any) -> Any:
        # Simulate downloading data from HTTP Connector
        print("Extracting data...")
        return {"city": "Milan", "temperature": 22.5, "humidity": "60"} # humidity is string, should be casted to int

    async def _transform(self, data: Any) -> Any:
        print("Transforming and Validating data...")
        # Validate against dynamic schema
        clean_data = self.registry.validate("WeatherMetric", data)
        return clean_data

    async def _load(self, data: Any) -> Any:
        print("Loading data into MongoDB...")
        # Simulate Mongo load
        return {"inserted_id": "5f1b2c3d", "data": data}

    async def run_weather_pipeline(self) -> dict:
        steps = [
            PipelineStep("Extract", self._extract),
            PipelineStep("Transform", self._transform),
            PipelineStep("Load", self._load)
        ]
        
        result = await self.orchestrator.execute_pipeline(
            name="Weather_ETL", 
            initial_data=None, 
            steps=steps
        )
        return result
