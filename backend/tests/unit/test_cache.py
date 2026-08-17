"""Unit tests: the bounded thread-safe TTL cache (Phase E hardening).

Verifies expiry, bounded eviction, memoisation semantics and a
concurrency smoke on ``get_or_compute`` — the primitive every hot
endpoint is backed by.
"""

from __future__ import annotations

import threading

from app.core.cache import TTLCache


class TestTTLCache:
    def test_get_returns_none_for_missing_key(self):
        cache = TTLCache(ttl_seconds=60)
        assert cache.get("missing") is None

    def test_set_then_get_roundtrip(self):
        cache = TTLCache(ttl_seconds=60)
        cache.set("a", {"value": 1})
        assert cache.get("a") == {"value": 1}

    def test_expired_entry_is_none(self):
        cache = TTLCache(ttl_seconds=0)
        cache.set("a", 1)
        assert cache.get("a") is None

    def test_get_or_compute_memoises(self):
        cache = TTLCache(ttl_seconds=60)
        calls = 0

        def compute():
            nonlocal calls
            calls += 1
            return "computed"

        assert cache.get_or_compute("k", compute) == "computed"
        assert cache.get_or_compute("k", compute) == "computed"
        assert calls == 1

    def test_get_or_compute_does_not_call_after_expiry(self):
        cache = TTLCache(ttl_seconds=0)
        calls = 0

        def compute():
            nonlocal calls
            calls += 1
            return "computed"

        cache.get_or_compute("k", compute)
        cache.get_or_compute("k", compute)
        assert calls == 2

    def test_max_entries_evicts_oldest(self):
        cache = TTLCache(ttl_seconds=60, max_entries=2)
        cache.set("a", 1)
        cache.set("b", 2)
        cache.set("c", 3)
        assert cache.get("a") is None  # oldest evicted
        assert cache.get("b") == 2
        assert cache.get("c") == 3

    def test_zero_max_entries_disables_storage(self):
        cache = TTLCache(ttl_seconds=60, max_entries=0)
        cache.set("a", 1)
        assert cache.get("a") is None

    def test_clear_removes_everything(self):
        cache = TTLCache(ttl_seconds=60)
        cache.set("a", 1)
        cache.clear()
        assert cache.get("a") is None

    def test_concurrent_get_or_compute_computes_once(self):
        cache = TTLCache(ttl_seconds=60, max_entries=64)
        barrier = threading.Barrier(8)
        calls = 0
        lock = threading.Lock()
        results: list[str] = []

        def compute():
            nonlocal calls
            with lock:
                calls += 1
            return "shared"

        def worker():
            barrier.wait()
            results.append(cache.get_or_compute("hot", compute))

        threads = [threading.Thread(target=worker) for _ in range(8)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

        assert results == ["shared"] * 8
        assert calls == 1
