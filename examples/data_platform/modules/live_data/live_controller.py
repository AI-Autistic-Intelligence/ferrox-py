from fastapi import APIRouter

from .live_service import LiveDataAggregatorService


class LiveController:
    def __init__(self, container):
        self.router = APIRouter(prefix="/live", tags=["Live Data Platform Demo"])
        self.container = container
        
        # Register the service in the IoC Container dynamically for the demo
        if LiveDataAggregatorService not in self.container._providers:
            self.container._providers[LiveDataAggregatorService] = LiveDataAggregatorService
        
        self.setup_routes()

    def setup_routes(self):
        @self.router.get("/dashboard")
        async def get_live_dashboard():
            """
            Fetches real-time aggregated data from Binance, GitHub, and Open-Meteo.
            Demonstrates Ferrox-Py's async I/O capabilities.
            """
            service: LiveDataAggregatorService = self.container.resolve(LiveDataAggregatorService)
            return await service.get_aggregated_dashboard()
