import time
from typing import Any, Dict
from fastapi import APIRouter, Response, status

from ..persistence import get_repository

START_TIME = time.time()


class HealthController:
    def __init__(self, container):
        self.router = APIRouter(tags=["Health & Observability"])
        self.container = container
        self.repo = get_repository()
        self.setup_routes()

    def setup_routes(self):
        @self.router.get(
            "/health",
            response_model=Dict[str, Any],
            summary="Service Health",
            description="Service health probe verifying that the application is running.",
        )
        @self.router.get(
            "/health/live",
            response_model=Dict[str, Any],
            summary="Liveness Probe",
            description="Kubernetes liveness probe verifying that the application process is running.",
        )
        async def liveness():
            return {
                "status": "UP",
                "uptime_seconds": round(time.time() - START_TIME, 2),
            }

        @self.router.get(
            "/health/ready",
            response_model=Dict[str, Any],
            summary="Readiness Probe",
            description="Kubernetes readiness probe verifying that the persistence layer and dependencies are operational.",
        )
        async def readiness(response: Response):
            db_ok = await self.repo.ping()
            overall = "UP" if db_ok else "DOWN"
            if not db_ok:
                response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE

            return {
                "status": overall,
                "checks": {
                    "database": "UP" if db_ok else "DOWN",
                },
                "uptime_seconds": round(time.time() - START_TIME, 2),
            }

        @self.router.get(
            "/metrics",
            summary="Prometheus Metrics",
            description="Exposes application telemetry in standard Prometheus exposition format.",
        )
        async def metrics():
            uptime = round(time.time() - START_TIME, 2)
            datasets = await self.repo.list_datasets(take=1000)
            ingestions = await self.repo.list_ingestions(limit=1000)
            runs = await self.repo.list_pipeline_runs(limit=1000)

            content = (
                f"# HELP ferrox_data_platform_uptime_seconds Process uptime in seconds\n"
                f"# TYPE ferrox_data_platform_uptime_seconds gauge\n"
                f"ferrox_data_platform_uptime_seconds {uptime}\n"
                f"# HELP ferrox_data_platform_datasets_total Total registered catalog datasets\n"
                f"# TYPE ferrox_data_platform_datasets_total gauge\n"
                f"ferrox_data_platform_datasets_total {len(datasets)}\n"
                f"# HELP ferrox_data_platform_ingestions_total Total ingestion records processed\n"
                f"# TYPE ferrox_data_platform_ingestions_total counter\n"
                f"ferrox_data_platform_ingestions_total {len(ingestions)}\n"
                f"# HELP ferrox_data_platform_pipeline_runs_total Total DAG pipeline executions\n"
                f"# TYPE ferrox_data_platform_pipeline_runs_total counter\n"
                f"ferrox_data_platform_pipeline_runs_total {len(runs)}\n"
            )
            return Response(content=content, media_type="text/plain; version=0.0.4")
