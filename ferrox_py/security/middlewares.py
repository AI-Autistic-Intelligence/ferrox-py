import re
import json
import logging
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response, JSONResponse
from .sentinel import SentinelThreatEngine

logger = logging.getLogger("sentinel")

class SentinelThreatEngineMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, threat_engine: SentinelThreatEngine = None):
        super().__init__(app)
        self.threat_engine = threat_engine or SentinelThreatEngine()
        self.sqli_pattern = re.compile(r'(\b(UNION|SELECT|INSERT|UPDATE|DELETE|DROP|ALTER)\b.*?\b(FROM|INTO|TABLE)\b)|(\'|%27).*?(--|#|\/\*)', re.IGNORECASE)
        self.xss_pattern = re.compile(r'(<(?:script|iframe|img|svg|object|embed).*?(?:src|onload|onerror)=)|(javascript:|vbscript:|data:text\/html)', re.IGNORECASE)
        self.rag_poisoning_pattern = re.compile(r'(ignore previous instructions|disregard|system prompt|you are now|forget everything|bypass|jailbreak)', re.IGNORECASE)

    async def dispatch(self, request: Request, call_next) -> Response:
        # We need to carefully consume the request body for inspection without preventing route from reading it
        try:
            body_bytes = await request.body()
            body_str = body_bytes.decode('utf-8', errors='ignore')
        except Exception:
            body_str = ""

        # Reconstruct request for downstream since we consumed body
        async def receive():
            return {"type": "http.request", "body": body_bytes}
        request._receive = receive

        query_str = str(request.query_params)
        payload_string = f"{body_str} {query_str}"

        try:
            # 1. Shannon Entropy Analysis (Obfuscated Shellcode detection)
            entropy = self.threat_engine.calculate_shannon_entropy(payload_string)
            if entropy > 4.9:
                self.flag_threat(f"High payload entropy ({entropy}) detected - Possible obfuscated shellcode")

            # 2. Advanced SQLi & XSS Heuristics
            if self.sqli_pattern.search(payload_string):
                self.flag_threat("SQL Injection Heuristic matched.")
            if self.xss_pattern.search(payload_string):
                self.flag_threat("XSS / Cross-Site Scripting Heuristic matched.")

            # 3. AI / RAG Prompt Injection Poisoning (LLM Security)
            if self.rag_poisoning_pattern.search(payload_string):
                self.flag_threat("AI/LLM Prompt Injection (RAG Poisoning) attempt detected.")

            # 4. Directory Traversal / LFI
            uri = str(request.url)
            if '../' in uri or '..\\\\' in uri or '/etc/passwd' in uri:
                self.flag_threat("Path Traversal / Local File Inclusion attempt detected in URI.")

        except Exception as e:
            logger.error(f"[SENTINEL WAF] BLOCK: {str(e)}")
            return JSONResponse({"error": "Forbidden", "message": "Ferrox Sentinel WAF Blocked Request: Security violation detected."}, status_code=403)

        return await call_next(request)

    def flag_threat(self, reason: str):
        raise Exception(reason)
