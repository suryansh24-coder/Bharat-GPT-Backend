import time
import uuid
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from app.utils.logger import logger

class SLATrackingMiddleware(BaseHTTPMiddleware):
    """
    Enterprise SLA Tracking & Distributed Tracing.
    Adds X-Trace-ID for distributed logging.
    Monitors SLA performance metrics and triggers alerts natively if thresholds break.
    """
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        trace_id = str(uuid.uuid4())
        
        request.state.trace_id = trace_id
        response = await call_next(request)
        
        process_time = time.time() - start_time
        response.headers["X-Trace-ID"] = trace_id
        response.headers["X-Process-Time"] = str(round(process_time, 4))
        
        # Enterprise SLA Rule: Log Performance Degradation (Responses slower than 1.5 seconds)
        if process_time > 1.5 and request.url.path not in ["/api/v1/chat/stream", "/health", "/metrics", "/ready"]:
            logger.warning(
                "SLA_VIOLATION_LATENCY",
                extra={
                    "trace_id": trace_id,
                    "url": str(request.url),
                    "process_time_ms": round(process_time * 1000, 2),
                    "alert": "Performance degradation reported."
                }
            )
            
        # Error Threshold alerts
        if response.status_code >= 500:
            logger.error(
                "SLA_VIOLATION_ERROR_RATE",
                extra={
                    "trace_id": trace_id,
                    "url": str(request.url),
                    "status_code": response.status_code,
                    "alert": "500 Internal Error threshold breached."
                }
            )
            
        return response
