from typing import Any, Callable, Dict, List, Optional, Type, Set, cast, AsyncGenerator, Any, Callable, Dict, List, Optional, Type, Set, cast, AsyncGenerator
import httpx
from fastapi import Request, Response
from ferrox_py.core.provider import injectable
from ferrox_py.core.errors import FerroxError

@injectable()
class ApiGatewayRouter:
    def __init__(self) -> None:
        self._routes: Dict[str, Any] = {}
        # We share one client for connection pooling
        self._client = httpx.AsyncClient()

    def add_route(self, path: str, downstream_url: str) -> Any:
        self._routes[path] = downstream_url

    async def proxy_request(self, path: str, request: Request) -> Response:
        downstream = self._routes.get(path)
        if not downstream:
            raise FerroxError(message="Route not found in API Gateway", status_code=404)
            
        url = f"{downstream}?{request.url.query}"
        
        # Read body stream
        body = await request.body()
        
        # Forward request
        res = await self._client.request(
            method=request.method,
            url=url,
            headers=Dict[Any, Any](request.headers),
            content=body
        )
        
        return Response(content=res.content, status_code=res.status_code, headers=Dict[Any, Any](res.headers))
