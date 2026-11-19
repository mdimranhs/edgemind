import asyncio
from collections import defaultdict, deque
import time
from fastapi import HTTPException, Request, status

from app.core.config import settings


class InMemoryRateLimiter:
    """Sliding-window rate limiter per client IP."""

    def __init__(self, requests_per_minute: int = 30) -> None:
        self.rpm = requests_per_minute
        self.requests: dict[str, deque[float]] = defaultdict(deque)
        self._lock = asyncio.Lock()

    def _extract_ip(self, request: Request) -> str:
        # Use the peer address after Uvicorn's trusted proxy middleware has
        # applied configured forwarding headers. Do not trust raw client input.
        if request.client and request.client.host:
            return request.client.host
        return "unknown"

    async def check(self, request: Request) -> None:
        client_ip = self._extract_ip(request)
        now = time.monotonic()
        window_start = now - 60.0

        async with self._lock:
            queue = self.requests[client_ip]
            while queue and queue[0] < window_start:
                queue.popleft()

            if len(queue) >= self.rpm:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Too many requests. Please wait a minute before trying again.",
                    headers={"Retry-After": "60"},
                )

            queue.append(now)

            if len(self.requests) > 1000:
                self._cleanup(window_start)

    def _cleanup(self, window_start: float) -> None:
        stale_ips = [
            ip for ip, queue in self.requests.items()
            if not queue or queue[-1] < window_start
        ]
        for ip in stale_ips:
            del self.requests[ip]


class ConcurrencyLimiter:
    """Limits the number of simultaneous active inference requests."""

    def __init__(self, max_concurrent: int = 4) -> None:
        self.semaphore = asyncio.Semaphore(max_concurrent)

    async def __aenter__(self):
        try:
            # Wait up to 2.0 seconds to acquire a concurrency slot
            await asyncio.wait_for(self.semaphore.acquire(), timeout=2.0)
        except asyncio.TimeoutError:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Server is currently handling maximum concurrent requests. Please retry in a few moments.",
                headers={"Retry-After": "5"},
            )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self.semaphore.release()


rate_limiter = InMemoryRateLimiter(requests_per_minute=settings.rate_limit_per_minute)
concurrency_limiter = ConcurrencyLimiter(max_concurrent=settings.max_concurrent_requests)

