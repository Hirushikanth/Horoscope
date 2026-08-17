"""Unit tests for serialization helpers and the TTL cache."""

from __future__ import annotations

import time

import numpy as np
from app.core.cache import TTLCache
from app.core.serialization import sanitize_numpy


class TestSanitizeNumpy:
    def test_np_float64_becomes_float(self):
        assert sanitize_numpy(np.float64(24.22)) == 24.22
        assert isinstance(sanitize_numpy(np.float64(1.0)), float)

    def test_np_integer_becomes_int(self):
        assert sanitize_numpy(np.int64(7)) == 7
        assert isinstance(sanitize_numpy(np.int64(7)), int)

    def test_np_bool_becomes_bool(self):
        assert sanitize_numpy(np.bool_(True)) is True

    def test_ndarray_becomes_list(self):
        arr = np.array([1.0, 2.0], dtype=np.float64)
        assert sanitize_numpy(arr) == [1.0, 2.0]
        assert isinstance(sanitize_numpy(arr), list)

    def test_nested_structures(self):
        data = {"a": np.float64(1.5), "b": [np.int64(2), np.bool_(True)]}
        clean = sanitize_numpy(data)
        assert clean == {"a": 1.5, "b": [2, True]}

    def test_plain_types_pass_through(self):
        assert sanitize_numpy("text") == "text"
        assert sanitize_numpy(42) == 42
        assert sanitize_numpy(None) is None


class TestTTLCache:
    def test_get_set_roundtrip(self):
        cache = TTLCache(ttl_seconds=60)
        cache.set("k", {"value": 1})
        assert cache.get("k") == {"value": 1}

    def test_missing_key_returns_none(self):
        cache = TTLCache()
        assert cache.get("missing") is None

    def test_expiry(self):
        cache = TTLCache(ttl_seconds=0.05)
        cache.set("k", "v")
        time.sleep(0.1)
        assert cache.get("k") is None

    def test_get_or_compute_caches(self):
        cache = TTLCache(ttl_seconds=60)
        calls = []

        def compute():
            calls.append(1)
            return "computed"

        assert cache.get_or_compute("k", compute) == "computed"
        assert cache.get_or_compute("k", compute) == "computed"
        assert len(calls) == 1

    def test_clear(self):
        cache = TTLCache()
        cache.set("k", 1)
        cache.clear()
        assert cache.get("k") is None

    def test_bounded_eviction(self):
        cache = TTLCache(ttl_seconds=60, max_entries=2)
        cache.set("a", 1)
        cache.set("b", 2)
        cache.set("c", 3)
        assert cache.get("a") is None
        assert cache.get("b") is not None
        assert cache.get("c") is not None
