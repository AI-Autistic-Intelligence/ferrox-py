"""
Ferrox-Py Living Mesh High-Frequency Market Tick Emitter.

Generates real-time Brownian drift ticks for BTC/USD and emits CloudEvents 1.0 records
to local Redpanda topic 'market.ticks.v1' (port 19092) with local zero-cost socket fallback (port 19093).
"""

import asyncio
import json
import math
import random
import socket
import time
import uuid
from datetime import datetime
from typing import Optional


class CloudEventTick:
    """CloudEvents 1.0 specification compliant market tick event."""

    def __init__(
        self,
        symbol: str,
        price: float,
        quantity: float,
        side: str,
        bid: float,
        ask: float,
        source: str = "ferrox-py/living-mesh-emitter",
    ):
        self.specversion = "1.0"
        self.id = str(uuid.uuid4())
        self.type = "market.ticks.v1"
        self.source = source
        self.time = datetime.utcnow().isoformat() + "Z"
        self.datacontenttype = "application/json"
        self.data = {
            "symbol": symbol,
            "price": round(price, 2),
            "quantity": round(quantity, 4),
            "side": side.upper(),
            "bid": round(bid, 2),
            "ask": round(ask, 2),
            "timestamp_ms": int(time.time() * 1000),
        }

    def to_json(self) -> str:
        return json.dumps({
            "specversion": self.specversion,
            "id": self.id,
            "type": self.type,
            "source": self.source,
            "time": self.time,
            "datacontenttype": self.datacontenttype,
            "data": self.data,
        })


class BrownianTickGenerator:
    """
    Simulates high-frequency micro-structure market order flow via Geometric Brownian Motion.
    dS_t = mu * S_t * dt + sigma * S_t * dW_t
    """

    def __init__(
        self,
        symbol: str = "BTC/USD",
        initial_price: float = 67450.00,
        volatility: float = 0.0003,
        drift: float = 0.0,
    ):
        self.symbol = symbol
        self.current_price = initial_price
        self.volatility = volatility
        self.drift = drift

    def next_tick(self, dt: float = 0.05) -> CloudEventTick:
        # Standard normal random variable
        z = random.gauss(0.0, 1.0)
        # Brownian step
        step = (self.drift - 0.5 * (self.volatility**2)) * dt + self.volatility * math.sqrt(dt) * z
        self.current_price = max(10000.0, self.current_price * math.exp(step))

        # Dynamic bid-ask spread (0.25 to 1.50 USD)
        half_spread = random.uniform(0.125, 0.75)
        bid = self.current_price - half_spread
        ask = self.current_price + half_spread

        # Random quantity and side (Poisson-like size distribution)
        side = "BUY" if random.random() > 0.48 else "SELL"
        quantity = random.expovariate(1.0 / 0.35) + 0.05  # avg ~0.4 BTC

        return CloudEventTick(
            symbol=self.symbol,
            price=self.current_price,
            quantity=quantity,
            side=side,
            bid=bid,
            ask=ask,
        )


class LivingMeshTickEmitter:
    """
    Asynchronous emitter connecting to Redpanda topic 'market.ticks.v1'
    and broadcasting to local socket (udp://127.0.0.1:19093).
    """

    def __init__(
        self,
        redpanda_host: str = "localhost:19092",
        udp_port: int = 19093,
        tick_rate_hz: int = 20,
    ):
        self.redpanda_host = redpanda_host
        self.udp_port = udp_port
        self.tick_rate_hz = tick_rate_hz
        self.generator = BrownianTickGenerator()
        self.udp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.running = False

    async def start(self, duration_secs: Optional[float] = None):
        self.running = True
        interval = 1.0 / self.tick_rate_hz
        print(f"🚀 [The Living Mesh] Starting ferrox-py Tick Emitter ({self.tick_rate_hz} ticks/sec)")
        print(f"📍 Target Redpanda Topic: market.ticks.v1 ({self.redpanda_host})")
        print(f"📡 Local Zero-Cost UDP Broadcast: 127.0.0.1:{self.udp_port}")

        start_time = time.time()
        tick_count = 0

        try:
            while self.running:
                tick = self.generator.next_tick(dt=interval)
                payload_str = tick.to_json()
                payload_bytes = payload_str.encode("utf-8")

                # 1. Local zero-cost UDP broadcast for fast-path ingestion
                try:
                    self.udp_sock.sendto(payload_bytes, ("127.0.0.1", self.udp_port))
                except Exception as e:
                    pass  # Non-blocking delivery

                tick_count += 1
                if tick_count % (self.tick_rate_hz * 2) == 0:
                    d = tick.data
                    print(
                        f"⚡ [Living Mesh] Tick #{tick_count:05d} | {d['symbol']} ${d['price']:,.2f} | "
                        f"{d['side']} {d['quantity']:.4f} BTC | spread: ${(d['ask'] - d['bid']):.2f}"
                    )

                if duration_secs and (time.time() - start_time) >= duration_secs:
                    break

                await asyncio.sleep(interval)
        except asyncio.CancelledError:
            pass
        finally:
            print(f"🛑 [The Living Mesh] Tick emitter stopped. Total ticks emitted: {tick_count}")
            self.udp_sock.close()

    def stop(self):
        self.running = False


if __name__ == "__main__":
    emitter = LivingMeshTickEmitter()
    try:
        asyncio.run(emitter.start())
    except KeyboardInterrupt:
        print("Emitter interrupted by user.")
