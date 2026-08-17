"""Concurrency smoke test — the API stays correct under parallel load.

Phase E hardening: concurrent jathakam requests must all succeed, return
identical payloads for identical inputs (the TTL cache is shared), and
never cross-contaminate results across different births.
"""

from __future__ import annotations

import threading

import pytest
from app.main import create_app
from fastapi.testclient import TestClient

BIRTH_A: dict = {
    "date": "1990-06-15",
    "time": "06:30:00",
    "timezone": "Asia/Colombo",
    "latitude": 6.9271,
    "longitude": 79.8612,
}
BIRTH_B: dict = {
    "date": "1985-01-02",
    "time": "14:15:00",
    "timezone": "Asia/Kolkata",
    "latitude": 13.0827,
    "longitude": 80.2707,
}

THREADS = 8
REQUESTS_PER_THREAD = 5


@pytest.fixture(scope="module")
def client() -> TestClient:
    """Module-scoped ASGI test client."""
    return TestClient(create_app())


class TestConcurrencySmoke:
    def test_identical_births_are_identical_under_concurrency(self, client):
        expected = client.post("/api/v2/jathakam", json=BIRTH_A).json()
        barrier = threading.Barrier(THREADS)
        failures: list[tuple[str, str]] = []

        def worker() -> None:
            barrier.wait()
            for _ in range(REQUESTS_PER_THREAD):
                response = client.post("/api/v2/jathakam", json=BIRTH_A)
                if response.status_code != 200:
                    failures.append(("status", str(response.status_code)))
                    return
                if response.json() != expected:
                    failures.append(("drift", response.text[:200]))
                    return

        threads = [threading.Thread(target=worker) for _ in range(THREADS)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

        assert not failures, failures

    def test_different_births_do_not_cross_contaminate(self, client):
        expected_a = client.post("/api/v2/jathakam", json=BIRTH_A).json()
        expected_b = client.post("/api/v2/jathakam", json=BIRTH_B).json()
        assert expected_a["birth"]["jd_ut1"] != expected_b["birth"]["jd_ut1"]

        barrier = threading.Barrier(THREADS)
        failures: list[str] = []

        def worker(birth: dict, expected: dict) -> None:
            barrier.wait()
            for _ in range(REQUESTS_PER_THREAD):
                response = client.post("/api/v2/jathakam", json=birth)
                if response.status_code != 200:
                    failures.append(f"status {response.status_code}")
                    return
                if response.json() != expected:
                    failures.append("cross-contamination")

        threads = [
            threading.Thread(target=worker, args=(BIRTH_A, expected_a)) for _ in range(THREADS // 2)
        ] + [
            threading.Thread(target=worker, args=(BIRTH_B, expected_b)) for _ in range(THREADS // 2)
        ]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

        assert not failures, failures
