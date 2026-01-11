"""
Simple in-memory cache implementation for query results.
"""
import time
from typing import Any, Optional, Dict
from dataclasses import dataclass
import hashlib


@dataclass
class CacheEntry:
    """Cache entry with value and expiration."""
    value: Any
    expires_at: float


class SimpleCache:
    """Thread-safe in-memory cache with TTL support."""

    def __init__(self, default_ttl: int = 3600):
        """
        Initialize cache.

        Args:
            default_ttl: Default time-to-live in seconds
        """
        self._cache: Dict[str, CacheEntry] = {}
        self._default_ttl = default_ttl

    def _generate_key(self, key: str) -> str:
        """Generate a hash key from string."""
        return hashlib.md5(key.encode()).hexdigest()

    def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found or expired
        """
        cache_key = self._generate_key(key)
        entry = self._cache.get(cache_key)

        if entry is None:
            return None

        # Check if expired
        if time.time() > entry.expires_at:
            del self._cache[cache_key]
            return None

        return entry.value

    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """
        Set value in cache.

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time-to-live in seconds (uses default if None)
        """
        cache_key = self._generate_key(key)
        expires_at = time.time() + (ttl or self._default_ttl)
        self._cache[cache_key] = CacheEntry(value=value, expires_at=expires_at)

    def delete(self, key: str) -> None:
        """
        Delete value from cache.

        Args:
            key: Cache key
        """
        cache_key = self._generate_key(key)
        self._cache.pop(cache_key, None)

    def clear(self) -> None:
        """Clear all cache entries."""
        self._cache.clear()

    def cleanup_expired(self) -> int:
        """
        Remove expired entries from cache.

        Returns:
            Number of entries removed
        """
        current_time = time.time()
        expired_keys = [
            key for key, entry in self._cache.items()
            if current_time > entry.expires_at
        ]

        for key in expired_keys:
            del self._cache[key]

        return len(expired_keys)


# Global cache instance
query_cache = SimpleCache()
