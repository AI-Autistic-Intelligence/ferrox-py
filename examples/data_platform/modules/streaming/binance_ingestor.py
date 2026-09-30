import asyncio
import json
import websockets
import redis.asyncio as redis
from pydantic import ValidationError
from structlog import get_logger
from .data_contracts import BinanceTradeContract, BinanceDepthContract, DataLineage

logger = get_logger()

# Multiplexed Binance WebSocket for multi-asset Trades & OrderBooks
# We ingest Trades for BTC, ETH, SOL (for Correlation & Whales)
# We ingest Depth5 for BTC, ETH, SOL (for OrderBook Imbalance/Spoofing)
STREAMS = [
    "btcusdt@trade", "ethusdt@trade", "solusdt@trade",
    "btcusdt@depth5@100ms", "ethusdt@depth5@100ms", "solusdt@depth5@100ms"
]
BINANCE_WS_URL = f"wss://stream.binance.com:9443/stream?streams={'/'.join(STREAMS)}"

REDIS_STREAM_TRADES = "ferrox:ingestion:crypto_trades"
REDIS_STREAM_DEPTH = "ferrox:ingestion:crypto_depth"

async def run_ingestion_engine():
    logger.info("Starting Multi-Asset High-Throughput Ingestion Engine...")
    
    r = redis.Redis(host='localhost', port=6379, decode_responses=True, socket_connect_timeout=1.0)
    use_redis = True
    try:
        await asyncio.wait_for(r.ping(), timeout=2.0)
        logger.info("Connected to Redis for Stream Backpressure.")
    except Exception:
        logger.warning("Redis not found or timed out. Running in Simulation/Print mode.")
        use_redis = False

    async for websocket in websockets.connect(BINANCE_WS_URL):
        logger.info("Connected to Binance Multiplexed WebSocket", streams=len(STREAMS))
        try:
            async for message in websocket:
                payload = json.loads(message)
                stream_name = payload.get("stream")
                raw_data = payload.get("data")
                
                if not stream_name or not raw_data:
                    continue
                    
                lineage = DataLineage(source_system="Binance_WS_API")
                
                # Route based on stream type
                try:
                    if "@trade" in stream_name:
                        contract = BinanceTradeContract(**raw_data)
                        contract.lineage = lineage
                        
                        if use_redis:
                            await r.xadd(REDIS_STREAM_TRADES, {"payload": contract.model_dump_json()}, maxlen=100000)
                        else:
                            logger.info("trade_ingested", symbol=contract.symbol, price=contract.price)
                            
                    elif "@depth5" in stream_name:
                        # Depth payload doesn't contain symbol, we extract it from stream name (e.g. btcusdt@depth5)
                        symbol = stream_name.split('@')[0].upper()
                        raw_data['symbol'] = symbol
                        contract = BinanceDepthContract(**raw_data)
                        contract.lineage = lineage
                        
                        if use_redis:
                            await r.xadd(REDIS_STREAM_DEPTH, {"payload": contract.model_dump_json()}, maxlen=50000)
                        else:
                            # Log just top bid/ask to avoid console spam
                            top_bid = contract.bids[0][0] if contract.bids else 0
                            top_ask = contract.asks[0][0] if contract.asks else 0
                            logger.info("depth_ingested", symbol=contract.symbol, top_bid=top_bid, top_ask=top_ask)
                            
                except ValidationError as e:
                    logger.error("schema_drift_detected", stream=stream_name, error=str(e))
                    continue
                    
        except websockets.ConnectionClosed:
            logger.warning("WebSocket Connection Closed. Reconnecting...")
            continue
        except Exception as e:
            logger.error("fatal_ingestion_error", error=str(e))
            break

if __name__ == "__main__":
    asyncio.run(run_ingestion_engine())
