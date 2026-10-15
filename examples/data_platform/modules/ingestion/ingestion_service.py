import asyncio
import os
import sys
from datetime import datetime, timezone
from typing import Any, Callable, Dict, List
from pydantic import BaseModel, ValidationError, create_model

from ferrox_py.core.errors import FerroxError
from ferrox_py.core.provider import injectable
from ..persistence import get_repository

# Attempt import from ferrox_py_utils, or look in workspace, or use built-in fallback
try:
    from ferrox_py_utils.pipelines.orchestrator import PipelineOrchestrator, PipelineStep
    from ferrox_py_utils.schemas.registry import SchemaRegistry
except ImportError:
    utils_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../../ferrox-py-utils"))
    if os.path.exists(utils_dir) and utils_dir not in sys.path:
        sys.path.insert(0, utils_dir)
    try:
        from ferrox_py_utils.pipelines.orchestrator import PipelineOrchestrator, PipelineStep
        from ferrox_py_utils.schemas.registry import SchemaRegistry
    except ImportError:
        class PipelineStep:
            def __init__(self, name: str, execute_fn: Callable[[Any], Any]):
                self.name = name
                self.execute_fn = execute_fn

        class PipelineOrchestrator:
            async def execute_pipeline(self, name: str, initial_data: Any, steps: List[PipelineStep]) -> Any:
                current_data = initial_data
                for step in steps:
                    if asyncio.iscoroutinefunction(step.execute_fn):
                        current_data = await step.execute_fn(current_data)
                    else:
                        current_data = step.execute_fn(current_data)
                return current_data

        class SchemaRegistry:
            def __init__(self) -> None:
                self._schemas: Dict[str, type[BaseModel]] = {}

            def register_schema(self, name: str, schema_def: Dict[str, Any]) -> None:
                self._schemas[name] = create_model(name, **schema_def)

            def validate(self, name: str, data: Dict[str, Any]) -> Dict[str, Any]:
                if name not in self._schemas:
                    raise FerroxError(message=f"Schema {name} not found", status_code=404)
                model = self._schemas[name]
                try:
                    instance = model(**data)
                    return instance.model_dump()
                except ValidationError as e:
                    raise FerroxError(message=f"Schema validation failed: {e.errors()}", status_code=400)


@injectable()
class IngestionService:
    def __init__(self):
        self.orchestrator = PipelineOrchestrator()
        self.registry = SchemaRegistry()
        self.repo = get_repository()

        # Register dynamic schema for weather metrics
        self.registry.register_schema(
            "WeatherMetric",
            {
                "city": (str, ...),
                "temperature": (float, ...),
                "humidity": (int, ...),
            },
        )

    async def _extract(self, payload: Any) -> Any:
        # Simulate downloading data from HTTP Connector / Open-Meteo
        return {
            "city": "Milan",
            "temperature": 22.5,
            "humidity": "60",  # string that will be validated and converted to int
            "recorded_at": datetime.now(timezone.utc).isoformat(),
        }

    async def _transform(self, data: Any) -> Any:
        # Validate against dynamic schema
        clean_data = self.registry.validate("WeatherMetric", data)
        return clean_data

    async def _load(self, data: Any) -> Any:
        # Persist loaded data to PostgreSQL or In-Memory repository
        record = await self.repo.record_ingestion(
            pipeline_name="Weather_ETL",
            source="Open-Meteo REST API",
            payload=data,
            status="success",
        )
        return {"inserted_id": record["id"], "data": data, "ingested_at": record["ingested_at"]}

    async def run_weather_pipeline(self) -> Dict[str, Any]:
        steps = [
            PipelineStep("Extract", self._extract),
            PipelineStep("Transform", self._transform),
            PipelineStep("Load", self._load),
        ]

        result = await self.orchestrator.execute_pipeline(
            name="Weather_ETL",
            initial_data=None,
            steps=steps,
        )
        return result
