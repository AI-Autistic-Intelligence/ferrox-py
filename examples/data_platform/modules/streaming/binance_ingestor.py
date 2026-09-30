import asyncio
import json
import websockets
import redis.asyncio as redis
from pydantic import ValidationError
from structlog import get_logger
from .data_contracts import BinanceTradeContract, DataLineage

logger = get_logger()

# Binance Public WebSocket (High Volume Stream)
BINANCE_WS_URL = "wss://stream.binance.com:9443/ws/btcusdt@trade"

# Redis Stream Key for Backpressure
REDIS_STREAM_KEY = "ferrox:ingestion:crypto_trades"

async def run_ingestion_engine():
    """
    Solves Point 2 (Backpressure):
    Connects to high-volume WebSocket, validates via Contract, and appends to a Redis Stream.
    If the consumer is slow, Redis buffers the stream, preventing memory crashes.
    """
    logger.info("Starting High-Throughput Ingestion Engine...")
    
    # Connect to Redis with a short timeout
    r = redis.Redis(host='localhost', port=6379, decode_responses=True, socket_connect_timeout=1.0)
    
    # Try connecting to Redis, if fails, just simulate it for demo
    use_redis = True
    try:
        await asyncio.wait_for(r.ping(), timeout=2.0)
        logger.info("Connected to Redis for Stream Backpressure.")
    except Exception:
        logger.warning("Redis not found or timed out. Running in Simulation/Print mode.")
        use_redis = False

    async for websocket in websockets.connect(BINANCE_WS_URL):
        logger.info("Connected to Binance WebSocket", url=BINANCE_WS_URL)
        try:
            async for message in websocket:
                raw_data = json.loads(message)
                
                # 1. Enforce Data Contract (Schema Validation)
                try:
                    contract = BinanceTradeContract(**raw_data)
                except ValidationError as e:
                    logger.error("schema_drift_detected", error=str(e), raw_data=raw_data)
                    continue # Skip invalid data (or send to a Dead Letter Queue)
                
                # 3. Inject Data Lineage
                contract.lineage = DataLineage(source_system="Binance_WS_API")
                
                # Serialize back to JSON for storage
                safe_payload = contract.model_dump_json()
                
                # 2. Handle Backpressure via Redis Streams
                if use_redis:
                    # Append to stream with a max length to prevent unbounded growth (e.g. 100k events)
                    await r.xadd(REDIS_STREAM_KEY, {"payload": safe_payload}, maxlen=100000)
                    logger.debug("ingested_to_stream", symbol=contract.symbol, price=contract.price)
                else:
                    logger.info("ingested_event", symbol=contract.symbol, price=contract.price, lineage=contract.lineage.model_dump())
                    
        except websockets.ConnectionClosed:
            logger.warning("WebSocket Connection Closed. Reconnecting...")
            continue
        except Exception as e:
            logger.error("fatal_ingestion_error", error=str(e))
            break

if __name__ == "__main__":
    asyncio.run(run_ingestion_engine())
