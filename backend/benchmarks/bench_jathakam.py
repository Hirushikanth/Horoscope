"""
bench_jathakam.py — latency benchmark for the flagship jathakam endpoint.

Measures latency of ``POST /api/v2/jathakam`` (via the FastAPI test
client, which exercises the full stack: schema validation, domain
services, DE440 ephemeris, JSON serialization) in two phases:

* **cached** — repeated identical requests (the hot-path p95 a user
  experiences once the TTL cache is warm);
* **compute** — unique birth instants per request, so every call runs
  the full ephemeris computation (the Phase E target: **p95 < 1 s**).

Usage:
    python benchmarks/bench_jathakam.py [--requests N] [--sample BIRTH_JSON]

Exit code is non-zero if the compute-phase p95 target is missed
(CI-friendly).
"""

from __future__ import annotations

import argparse
import json
import statistics
import sys
import time
from pathlib import Path

from app.main import create_app
from fastapi.testclient import TestClient

DEFAULT_BIRTH = {
    "date": "1990-06-15",
    "time": "06:30:00",
    "timezone": "Asia/Colombo",
    "latitude": 6.9271,
    "longitude": 79.8612,
}

P95_TARGET_SECONDS = 1.0


def _percentile(values: list[float], pct: float) -> float:
    ordered = sorted(values)
    index = min(len(ordered) - 1, int(len(ordered) * pct / 100.0))
    return ordered[index]


def _summarize(latencies: list[float]) -> dict[str, float]:
    return {
        "requests": float(len(latencies)),
        "min": min(latencies),
        "mean": statistics.mean(latencies),
        "p50": _percentile(latencies, 50),
        "p95": _percentile(latencies, 95),
        "p99": _percentile(latencies, 99),
        "max": max(latencies),
    }


def run_benchmark(requests: int, birth: dict) -> dict[str, dict[str, float]]:
    """Measure the cached hot path and the cold-cache compute path."""
    client = TestClient(create_app())

    # Warm up: cold ephemeris load and cache fill must not distort the sample.
    response = client.post("/api/v2/jathakam", json=birth)
    if response.status_code != 200:
        raise RuntimeError(f"jathakam returned {response.status_code}: {response.text[:200]}")

    cached: list[float] = []
    for _ in range(requests):
        started = time.perf_counter()
        response = client.post("/api/v2/jathakam", json=birth)
        cached.append(time.perf_counter() - started)
        if response.status_code != 200:
            raise RuntimeError(f"jathakam returned {response.status_code}: {response.text[:200]}")

    # Unique birth instants (1-second step) — every request misses the cache.
    compute: list[float] = []
    base_minutes = birth.get("time", "00:00:00")
    parts = base_minutes.split(":")[:2]
    hour, minute = (int(part) for part in parts)
    for index in range(requests):
        minutes = (minute + index) % 60
        hours = (hour + (minute + index) // 60) % 24
        unique = {**birth, "time": f"{hours:02d}:{minutes:02d}:00"}
        started = time.perf_counter()
        response = client.post("/api/v2/jathakam", json=unique)
        compute.append(time.perf_counter() - started)
        if response.status_code != 200:
            raise RuntimeError(f"jathakam returned {response.status_code}: {response.text[:200]}")

    return {"cached": _summarize(cached), "compute": _summarize(compute)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--requests", type=int, default=30, help="number of timed requests")
    parser.add_argument("--sample", type=Path, default=None, help="path to a JSON birth sample")
    args = parser.parse_args()

    birth = DEFAULT_BIRTH
    if args.sample is not None:
        birth = json.loads(args.sample.read_text(encoding="utf-8"))

    stats = run_benchmark(args.requests, birth)
    print(json.dumps(stats, indent=2))

    compute_p95 = stats["compute"]["p95"]
    status = "PASS" if compute_p95 < P95_TARGET_SECONDS else "FAIL"
    print(
        f"\ncompute p95 {compute_p95 * 1000:.1f} ms "
        f"vs target {P95_TARGET_SECONDS * 1000:.0f} ms -> {status}"
    )
    return 0 if status == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
