import asyncio
from typing import AsyncGenerator, Callable
from fastapi.responses import StreamingResponse
from ferrox_py.core.provider import injectable

@injectable()
class SSEService:
    def stream(self, generator_func: Callable[[], AsyncGenerator[str, None]]) -> StreamingResponse:
        """
        Creates a Server-Sent Events response from an async generator.
        """
        async def format_sse():
            async for data in generator_func():
                # SSE format requires data: payload \n\n
                yield f"data: {data}\n\n"
                
        return StreamingResponse(format_sse(), media_type="text/event-stream")
