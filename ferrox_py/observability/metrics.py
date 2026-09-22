from prometheus_client import Counter, Histogram
from ferrox_py.core.provider import injectable

@injectable()
class MetricsService:
    def __init__(self):
        self.http_requests_total = Counter(
            'http_requests_total', 
            'Total HTTP Requests', 
            ['method', 'endpoint', 'status']
        )
        self.http_request_duration_seconds = Histogram(
            'http_request_duration_seconds', 
            'HTTP Request Duration', 
            ['method', 'endpoint']
        )

    def record_request(self, method: str, endpoint: str, status: int, duration: float):
        self.http_requests_total.labels(method=method, endpoint=endpoint, status=status).inc()
        self.http_request_duration_seconds.labels(method=method, endpoint=endpoint).observe(duration)
