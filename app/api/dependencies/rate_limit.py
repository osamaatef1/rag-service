"""
Rate limiting dependency for API routes.
"""
import time
from collections import defaultdict
from typing import Dict
from fastapi import HTTPException, Request, status
from app.core.config import get_settings

settings = get_settings()


class RateLimiter:
    """Simple in-memory rate limiter."""

    def __init__(self):
        """Initialize rate limiter."""
        self._requests: Dict[str, list] = defaultdict(list)

    def check_rate_limit(self, client_id: str) -> bool:
        """
        Check if client has exceeded rate limit.

        Args:
            client_id: Unique client identifier (e.g., IP address)

        Returns:
            True if within limit, False if exceeded
        """
        current_time = time.time()
        minute_ago = current_time - 60

        # Clean old requests
        self._requests[client_id] = [
            req_time for req_time in self._requests[client_id]
            if req_time > minute_ago
        ]

        # Check limit
        if len(self._requests[client_id]) >= settings.RATE_LIMIT_PER_MINUTE:
            return False

        # Add current request
        self._requests[client_id].append(current_time)
        return True


# Global rate limiter instance
rate_limiter = RateLimiter()


async def check_rate_limit(request: Request):
    """
    Dependency to check rate limit for incoming requests.

    Args:
        request: FastAPI request object

    Raises:
        HTTPException: If rate limit exceeded
    """
    client_id = request.client.host

    if not rate_limiter.check_rate_limit(client_id):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Please try again later."
        )
