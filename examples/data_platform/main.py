import os
import uvicorn
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from modules.analytics.quant_controller import QuantController
from modules.catalog.catalog_controller import CatalogController
from modules.etl.etl_controller import EtlController
from modules.ingestion.ingestion_controller import IngestionController
from modules.live_data.live_controller import LiveController
from modules.health.health_controller import HealthController
from modules.common.logging_middleware import StructuredJsonLoggingMiddleware

from ferrox_py.core.container import Container
from ferrox_py.security.middlewares import SentinelThreatEngineMiddleware


def create_app() -> FastAPI:
    app = FastAPI(
        title="Ferrox Enterprise Data Platform",
        description=(
            "Production-ready reference data engineering platform built on Ferrox-Py. "
            "Features asynchronous DAG orchestration, metadata cataloging with dual-mode persistence "
            "(In-Memory / PostgreSQL), token bucket rate limiting, Sentinel Threat protection, "
            "and OpenTelemetry-compatible structured JSON logging."
        ),
        version="2.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_tags=[
            {"name": "Health & Observability", "description": "Liveness, readiness probes and Prometheus metrics"},
            {"name": "Data Catalog", "description": "Dataset schema registry and metadata management"},
            {"name": "Data Ingestion", "description": "Stream and batch ingestion pipelines with validation"},
            {"name": "Data Pipelines (DAGs)", "description": "Directed Acyclic Graph parallel execution engine"},
            {"name": "Quantitative Analysis", "description": "High-frequency market signal generation"},
            {"name": "Live Data Platform Demo", "description": "Real-time aggregated market and weather feeds"},
        ],
    )

    # 1. Register Middlewares
    app.add_middleware(StructuredJsonLoggingMiddleware)
    app.add_middleware(SentinelThreatEngineMiddleware)

    # 2. Mount Static Files for the Dashboard
    static_dir = os.path.join(os.path.dirname(__file__), "static")
    if os.path.exists(static_dir):
        app.mount("/static", StaticFiles(directory=static_dir), name="static")

        @app.get("/", include_in_schema=False)
        async def serve_dashboard():
            return FileResponse(os.path.join(static_dir, "index.html"))

    # 3. Boot IoC Container
    container = Container()

    # 4. Instantiate Controllers
    health = HealthController(container)
    ingest = IngestionController(container)
    catalog = CatalogController(container)
    live = LiveController(container)
    etl = EtlController(container)
    quant = QuantController(container)

    # 5. Mount Routes
    app.include_router(health.router)
    app.include_router(catalog.router)
    app.include_router(ingest.router)
    app.include_router(etl.router)
    app.include_router(quant.router)
    app.include_router(live.router)

    return app


app = create_app()

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
