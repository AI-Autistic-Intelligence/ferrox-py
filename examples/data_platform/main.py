import uvicorn
from fastapi import FastAPI
from ferrox_py.core.container import Container
from modules.ingestion.ingestion_controller import IngestionController
from modules.catalog.catalog_controller import CatalogController
from modules.live_data.live_controller import LiveController
from modules.etl.etl_controller import EtlController

def create_app() -> FastAPI:
    app = FastAPI(title="Ferrox Data Platform")
    
    # 1. Boot IoC Container
    container = Container()
    
    # 2. Register Controllers
    ingest = IngestionController(container)
    catalog = CatalogController(container)
    live = LiveController(container)
    etl = EtlController(container)
    
    # 3. Mount Routes
    app.include_router(ingest.router)
    app.include_router(catalog.router)
    app.include_router(live.router)
    app.include_router(etl.router)
    
    return app

app = create_app()

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
