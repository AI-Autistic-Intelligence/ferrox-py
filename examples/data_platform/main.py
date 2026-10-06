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

from ferrox_py.core.container import Container


def create_app() -> FastAPI:
    app = FastAPI(title="Ferrox Data Platform")
    
    # Mount Static Files for the Dashboard
    static_dir = os.path.join(os.path.dirname(__file__), "static")
    if os.path.exists(static_dir):
        app.mount("/static", StaticFiles(directory=static_dir), name="static")
    
    @app.get("/")
    async def serve_dashboard():
        return FileResponse(os.path.join(static_dir, "index.html"))
    
    # 1. Boot IoC Container
    container = Container()
    
    # 2. Register Controllers
    ingest = IngestionController(container)
    catalog = CatalogController(container)
    live = LiveController(container)
    etl = EtlController(container)
    quant = QuantController(container)
    
    # 3. Mount Routes
    app.include_router(ingest.router)
    app.include_router(catalog.router)
    app.include_router(live.router)
    app.include_router(etl.router)
    app.include_router(quant.router)
    
    return app

app = create_app()

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
