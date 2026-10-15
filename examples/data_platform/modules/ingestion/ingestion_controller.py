from typing import Any, Dict, List, Optional
from fastapi import HTTPException, Query, Request, status
from pydantic import BaseModel, Field

from ferrox_py.core.container import Container
from ferrox_py.core.controllers import BaseController
from ferrox_py.security.rate_limiting import RateLimiter

from .ingestion_service import IngestionService
from ..persistence import get_repository


class CustomIngestRequest(BaseModel):
    source: str = Field(..., description="Source origin of the event stream", json_schema_extra={"example": "iot_gateway_01"})
    payload: Dict[str, Any] = Field(..., description="Arbitrary JSON telemetry payload", json_schema_extra={"example": {"sensor_id": "SN-9812", "metric": "pressure_psi", "val": 104.2}})


class IngestionController(BaseController):
    def __init__(self, container: Container):
        super().__init__(prefix="/ingest", tags=["Data Ingestion"])
        self.service = IngestionService()
        self.rate_limiter = RateLimiter()
        self.repo = get_repository()

        @self.router.post(
            "/trigger/weather",
            response_model=Dict[str, Any],
            summary="Trigger Weather Ingestion Pipeline",
            description="Executes the 3-stage weather pipeline: Extract (Open-Meteo), Transform (Schema Validation), and Load (Persistence). Rate-limited by Token Bucket.",
        )
        async def trigger_weather_etl(request: Request):
            client_ip = request.client.host if request.client else "unknown"

            # Rate limit: 5 requests per second
            allowed = await self.rate_limiter.is_allowed(f"etl_{client_ip}", capacity=5, refill_rate=2.0)
            if not allowed:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Rate limit exceeded: 5 requests per second permitted.",
                )

            result = await self.service.run_weather_pipeline()
            return self.ok(result, "Pipeline executed successfully")

        @self.router.post(
            "/custom",
            response_model=Dict[str, Any],
            status_code=status.HTTP_201_CREATED,
            summary="Ingest Custom Telemetry Event",
            description="Directly ingests an arbitrary JSON payload into the persistence layer with correlation and audit tracking.",
        )
        async def ingest_custom_event(payload: CustomIngestRequest):
            record = await self.repo.record_ingestion(
                pipeline_name="Custom_Direct_Ingest",
                source=payload.source,
                payload=payload.payload,
                status="success",
            )
            return self.ok(record, "Telemetry event ingested successfully")

        @self.router.get(
            "/history",
            response_model=Dict[str, Any],
            summary="Get Recent Ingestion History",
            description="Retrieves the most recent data ingestion events from the persistence layer.",
        )
        async def get_ingestion_history(
            limit: int = Query(20, ge=1, le=100, description="Maximum number of historical records to return"),
        ):
            records = await self.repo.list_ingestions(limit=limit)
            return self.ok({"total": len(records), "records": records}, "Ingestion history retrieved")
