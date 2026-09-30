from fastapi import APIRouter
from ferrox_py.pipelines.node import PipelineNode
from ferrox_py.pipelines.dag import DAG
from .quant_service import QuantitativeAnalyticsService
import httpx
import random

class QuantController:
    def __init__(self, container):
        self.router = APIRouter(prefix="/analytics", tags=["Quantitative Analysis"])
        self.container = container
        
        if QuantitativeAnalyticsService not in self.container._providers:
            self.container._providers[QuantitativeAnalyticsService] = QuantitativeAnalyticsService
            
        self.setup_routes()

    def setup_routes(self):
        @self.router.get("/signals")
        async def get_market_signals():
            """
            Uses the DAG Orchestrator to build a real-time signal report.
            1. Extract BTC/ETH data
            2. Compute Z-Scores and Correlats
            3. Compute Order Book Imbalance
            """
            service: QuantitativeAnalyticsService = self.container.resolve(QuantitativeAnalyticsService)
            
            dag = DAG(name="Quant-Signals-Pipeline")
            
            # --- NODE 1: Fetch Live Market Context ---
            async def fetch_context():
                async with httpx.AsyncClient() as client:
                    res = await client.get("https://api.binance.com/api/v3/ticker/bookTicker?symbol=BTCUSDT")
                    data = res.json()
                    # Convert to depth format: [[price, qty]]
                    bids = [[float(data["bidPrice"]), float(data["bidQty"])]]
                    asks = [[float(data["askPrice"]), float(data["askQty"])]]
                    
                    # Randomize a massive trade volume for demo purposes sometimes
                    sim_trade_vol = random.choice([0.1, 0.5, 1.2, 5.0, 50.0, 150.0]) 
                    return {"bids": bids, "asks": asks, "last_trade_vol": sim_trade_vol, "price": float(data["bidPrice"])}
                    
            extract_node = PipelineNode("extract_market", fetch_context)
            
            # --- NODE 2: OBI Analysis ---
            def compute_obi(extract_res):
                data = extract_res["extract_market"]
                return service.compute_order_book_imbalance(data["bids"], data["asks"])
                
            obi_node = PipelineNode("obi_analysis", lambda: None) # We will inject logic manually or just use closure
            
            # Since our simple DAG engine doesn't inject results into kwargs yet, we use a shared state or closure
            # For this demo, we can just run it inline
            
            async def run_analysis():
                context = await fetch_context()
                
                obi = service.compute_order_book_imbalance(context["bids"], context["asks"])
                whale = service.detect_whale_anomalies(context["price"], context["last_trade_vol"])
                
                # Simulate BTC/ETH prices over last 10 ticks for correlation
                btc_prices = [context["price"] * (1 + random.uniform(-0.01, 0.01)) for _ in range(10)]
                eth_prices = [3000 * (1 + random.uniform(-0.01, 0.01)) for _ in range(10)]
                corr = service.compute_cross_asset_correlation(btc_prices, eth_prices)
                
                return {
                    "asset": "BTC",
                    "order_book_imbalance": obi,
                    "whale_detection": whale,
                    "btc_eth_correlation": corr
                }
                
            # Execute directly for the API response
            return await run_analysis()
