"""
Rate Limiting Middleware - 100 requests per minute per IP
"""

import time
from typing import Dict, List, Tuple
from collections import defaultdict
from threading import Lock

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limiting middleware - 100 requests per minute per IP"""

    def __init__(self, app, requests_per_minute: int = 100):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.requests: Dict[str, List[float]] = defaultdict(list)
        self.lock = Lock()

    def cleanup_old_requests(self, ip: str, current_time: float):
        """Remove requests older than 1 minute"""
        cutoff = current_time - 60
        self.requests[ip] = [t for t in self.requests[ip] if t > cutoff]

    def is_rate_limited(self, ip: str) -> Tuple[bool, int]:
        """Check if IP is rate limited"""
        current_time = time.time()
        with self.lock:
            self.cleanup_old_requests(ip, current_time)
            request_count = len(self.requests[ip])

            if request_count >= self.requests_per_minute:
                # Find when the oldest request will expire
                oldest = min(self.requests[ip]) if self.requests[ip] else current_time
                retry_after = int(oldest + 60 - current_time) + 1
                return True, retry_after

            self.requests[ip].append(current_time)
            return False, 0

    async def dispatch(self, request: Request, call_next):
        # Skip rate limiting for WebSocket and health endpoints
        if request.url.path in ["/ws", "/health"] or request.url.path.startswith("/ws"):
            return await call_next(request)

        client_ip = request.client.host if request.client else "unknown"
        limited, retry_after = self.is_rate_limited(client_ip)

        if limited:
            return JSONResponse(
                status_code=429,
                content={
                    "error": "Rate limit exceeded",
                    "retry_after": retry_after,
                    "message": f"Too many requests. Retry in {retry_after} seconds."
                },
                headers={"Retry-After": str(retry_after)}
            )

        response = await call_next(request)
        return response
