from typing import Dict, Tuple
from time import time
from collections import defaultdict
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
import logging

logger = logging.getLogger(__name__)

# In-memory rate limit storage (use Redis in production)
_rate_limit_store: Dict[str, list[float]] = defaultdict(list)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Simple rate limiting middleware.
    Limits requests per IP address.
    """
    
    def __init__(
        self,
        app,
        requests_per_minute: int = 60,
        requests_per_hour: int = 1000
    ):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.requests_per_hour = requests_per_hour
    
    async def dispatch(self, request: Request, call_next):
        # Skip rate limiting for health check and static files
        if request.url.path in ["/health", "/docs", "/openapi.json", "/redoc"] or request.url.path.startswith("/static"):
            return await call_next(request)
        
        # Get client IP
        client_ip = request.client.host if request.client else "unknown"
        
        # Check rate limits
        now = time()
        minute_ago = now - 60
        hour_ago = now - 3600
        
        # Clean old entries
        _rate_limit_store[client_ip] = [
            timestamp for timestamp in _rate_limit_store[client_ip]
            if timestamp > hour_ago
        ]
        
        # Count requests in last minute
        recent_requests = [
            timestamp for timestamp in _rate_limit_store[client_ip]
            if timestamp > minute_ago
        ]
        
        if len(recent_requests) >= self.requests_per_minute:
            logger.warning(f"Rate limit exceeded for IP {client_ip}: {len(recent_requests)} requests in last minute")
            return Response(
                content='{"error": {"message": "Rate limit exceeded. Please try again later.", "type": "RateLimitError"}}',
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                media_type="application/json",
                headers={
                    "X-RateLimit-Limit": str(self.requests_per_minute),
                    "X-RateLimit-Remaining": "0",
                    "Retry-After": "60"
                }
            )
        
        # Count requests in last hour
        hourly_requests = len(_rate_limit_store[client_ip])
        if hourly_requests >= self.requests_per_hour:
            logger.warning(f"Hourly rate limit exceeded for IP {client_ip}: {hourly_requests} requests in last hour")
            return Response(
                content='{"error": {"message": "Hourly rate limit exceeded. Please try again later.", "type": "RateLimitError"}}',
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                media_type="application/json",
                headers={
                    "X-RateLimit-Limit": str(self.requests_per_hour),
                    "X-RateLimit-Remaining": "0",
                    "Retry-After": "3600"
                }
            )
        
        # Record this request
        _rate_limit_store[client_ip].append(now)
        
        # Process request
        response = await call_next(request)
        
        # Add rate limit headers
        remaining_minute = max(0, self.requests_per_minute - len(recent_requests) - 1)
        remaining_hour = max(0, self.requests_per_hour - hourly_requests - 1)
        
        response.headers["X-RateLimit-Limit-Minute"] = str(self.requests_per_minute)
        response.headers["X-RateLimit-Remaining-Minute"] = str(remaining_minute)
        response.headers["X-RateLimit-Limit-Hour"] = str(self.requests_per_hour)
        response.headers["X-RateLimit-Remaining-Hour"] = str(remaining_hour)
        
        return response


def clear_rate_limits():
    """Clear all rate limit data (useful for testing)."""
    _rate_limit_store.clear()

