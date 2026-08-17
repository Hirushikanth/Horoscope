"""
cache.py — lightweight thread-safe TTL cache.

Used to memoise expensive computed results (e.g. complete jathakams)
keyed by request fingerprint. Entries expire after a configurable TTL
and the cache is bounded to a maximum number of entries.
"""

from __future__ import annotations

import threading
import time
from collections.abc import Callable


class TTLCache[T]:
    """A bounded, thread-safe, time-to-live cache."""

    def __init__(self, ttl_seconds: int = 300, max_entries: int = 1024) -> None:
        self._ttl = ttl_seconds
        self._max_entries = max_entries
        self._data: dict[str, tuple[float, T]] = {}
        self._lock = threading.Lock()

    def get(self, key: str) -> T | None:
        """Return the cached value if fresh, else ``None``."""
        with self._lock:
            entry = self._data.get(key)
            if entry is None:
                return None
            expires_at, value = entry
            if time.monotonic() > expires_at:
                del self._data[key]
                return None
            return value

    def set(self, key: str, value: T) -> None:
        """Store a value with the cache's TTL, evicting stale/oldest entries."""
        with self._lock:
            if self._max_entries <= 0:
                return
            if len(self._data) >= self._max_entries:
                self._evict_one()
            self._data[key] = (time.monotonic() + self._ttl, value)

    def get_or_compute(self, key: str, compute: Callable[[], T]) -> T:
        """Return the cached value or compute, store, and return it."""
        cached = self.get(key)
        if cached is not None:
            return cached
        value = compute()
        self.set(key, value)
        return value

    def clear(self) -> None:
        """Remove all entries."""
        with self._lock:
            self._data.clear()

    def _evict_one(self) -> None:
        now = time.monotonic()
        oldest_key: str | None = None
        oldest_expiry = float("inf")
        for key, (expires_at, _) in list(self._data.items()):
            if expires_at <= now:
                oldest_key = key
                break
            if expires_at < oldest_expiry:
                oldest_expiry = expires_at
                oldest_key = key
        if oldest_key is not None:
            del self._data[oldest_key]
