from fastapi import Request

from ferrox_py.core.container import Container
from ferrox_py.core.controllers import BaseController
from ferrox_py.security.rate_limiting import RateLimiter

from .ingestion_service import IngestionService


class IngestionController(BaseController):
    def __init__(self, container: Container):
        super().__init__(prefix="/ingest", tags=["Ingestion"])
        
        self.service = IngestionService()
        self.rate_limiter = RateLimiter()
        
        @self.router.post("/trigger/weather")
        async def trigger_weather_etl(request: Request):
            """
            Triggers a data pipeline to fetch weather data.
            Protected by Token Bucket Rate Limiting.
            """
            client_ip = request.client.host if request.client else "unknown"
            
            # Rate limit: 2 requests per second
            allowed = await self.rate_limiter.is_allowed(f"etl_{client_ip}", capacity=2, refill_rate=1.0)
            if not allowed:
                return {"status": "error", "message": "Too Many Requests", "code": 429}
                
            # Execute Pipeline
            result = await self.service.run_weather_pipeline()
            
            return self.ok(result, "Pipeline executed successfully")
