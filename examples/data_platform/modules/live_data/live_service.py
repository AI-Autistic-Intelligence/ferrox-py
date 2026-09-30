import httpx
import asyncio
from structlog import get_logger

logger = get_logger()

class LiveDataAggregatorService:
    """
    Demonstrates Ferrox-Py's capability to act as a high-performance Data Platform Edge.
    Fetches data concurrently from multiple public, free APIs.
    """
    
    async def fetch_crypto_price(self, client: httpx.AsyncClient) -> dict:
        try:
            # Binance public API (no key required for ticker)
            res = await client.get("https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT")
            res.raise_for_status()
            data = res.json()
            return {"asset": "BTC", "price_usd": float(data["price"])}
        except Exception as e:
            logger.error("failed_fetch_crypto", error=str(e))
            return {"asset": "BTC", "price_usd": None, "error": "API Unavailable"}

    async def fetch_github_status(self, client: httpx.AsyncClient) -> dict:
        try:
            # GitHub public API
            res = await client.get("https://www.githubstatus.com/api/v2/status.json")
            res.raise_for_status()
            data = res.json()
            return {"system": "GitHub", "status": data.get("status", {}).get("description")}
        except Exception as e:
            logger.error("failed_fetch_github", error=str(e))
            return {"system": "GitHub", "status": "Unknown"}

    async def fetch_weather_ny(self, client: httpx.AsyncClient) -> dict:
        try:
            # Open-Meteo (Free, no key)
            res = await client.get("https://api.open-meteo.com/v1/forecast?latitude=40.7143&longitude=-74.006&current_weather=true")
            res.raise_for_status()
            data = res.json()
            current = data.get("current_weather", {})
            return {"city": "New York", "temperature_celsius": current.get("temperature"), "windspeed": current.get("windspeed")}
        except Exception as e:
            logger.error("failed_fetch_weather", error=str(e))
            return {"city": "New York", "error": "Weather API Unavailable"}

    async def get_aggregated_dashboard(self) -> dict:
        """
        Aggregates data using asyncio.gather for lightning-fast concurrent I/O.
        """
        async with httpx.AsyncClient(timeout=5.0) as client:
            crypto_task = self.fetch_crypto_price(client)
            github_task = self.fetch_github_status(client)
            weather_task = self.fetch_weather_ny(client)
            
            # Execute all external calls concurrently (Scatter-Gather pattern)
            results = await asyncio.gather(crypto_task, github_task, weather_task)
            
            return {
                "platform": "Ferrox-Py Data Aggregator",
                "status": "Operational",
                "metrics": {
                    "markets": results[0],
                    "dev_ops": results[1],
                    "environment": results[2]
                }
            }
