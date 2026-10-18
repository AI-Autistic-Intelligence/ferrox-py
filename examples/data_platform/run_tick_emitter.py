#!/usr/bin/env python3
"""Runner for ferrox-py living mesh tick emitter."""

import asyncio
from modules.streaming.tick_emitter import LivingMeshTickEmitter

if __name__ == "__main__":
    emitter = LivingMeshTickEmitter(tick_rate_hz=20)
    try:
        asyncio.run(emitter.start())
    except KeyboardInterrupt:
        print("\nShutdown complete.")
