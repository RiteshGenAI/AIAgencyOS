import time
import logging
import collections
import threading

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger("agency_os")


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start = time.time()
        response = await call_next(request)
        duration = time.time() - start
        logger.info(
            "%s %s - %s - %.3fs",
            request.method,
            request.url.path,
            response.status_code,
            duration,
        )
        return response


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            return await call_next(request)
        except Exception:
            logger.exception("Unhandled error on %s %s", request.method, request.url.path)
            from fastapi.responses import JSONResponse

            return JSONResponse(
                status_code=500,
                content={"detail": "Internal server error"},
            )


class RateLimitingMiddleware(BaseHTTPMiddleware):
    """In-memory rate limiter for auth routes."""

    def __init__(self, app, limit: int = 15, window_seconds: int = 60):
        super().__init__(app)
        self.limit = limit
        self.window_seconds = window_seconds
        self.requests = collections.defaultdict(list)
        self.lock = threading.Lock()

    async def dispatch(self, request: Request, call_next):
        if request.url.path.startswith("/api/v1/auth/login") or request.url.path.startswith(
            "/api/v1/auth/signup"
        ):
            client_ip = request.client.host if request.client else "unknown"
            now = time.time()

            with self.lock:
                self.requests[client_ip] = [
                    t for t in self.requests[client_ip] if now - t < self.window_seconds
                ]
                if len(self.requests[client_ip]) >= self.limit:
                    from fastapi.responses import JSONResponse

                    return JSONResponse(
                        status_code=429,
                        content={"detail": "Too many requests. Please try again later."},
                    )
                self.requests[client_ip].append(now)

        return await call_next(request)
