"""Golden snapshot test — the yogatara stars payload is deterministic.

M5 exit criterion: ``POST /api/v2/stars`` returns proper-motion
corrected catalogue positions. The snapshot is committed to
``data/stars_snapshot.json`` and recomputed here; any drift in the
catalogue (Hipparcos values, proper-motion handling) or the payload
shape fails this test and requires deliberate regeneration.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest
from app.services.stars_service import StarsService

SNAPSHOT_PATH = Path(__file__).parent / "data" / "stars_snapshot.json"

#: Matches golden sample #2 of the Swiss Ephemeris suite.
BIRTH: dict[str, Any] = {
    "date": "1990-06-15",
    "time": "06:30:00",
    "timezone": "Asia/Colombo",
    "latitude": 6.9271,
    "longitude": 79.8612,
}


def _assert_same(expected: Any, actual: Any, path: str = "$") -> None:
    """Deep-compare; floats within 1e-12, everything else exactly."""
    if isinstance(expected, dict):
        assert isinstance(actual, dict), f"{path}: expected dict, got {type(actual).__name__}"
        assert set(actual) == set(expected), f"{path}: keys differ: {set(expected) ^ set(actual)}"
        for key in expected:
            _assert_same(expected[key], actual[key], f"{path}.{key}")
    elif isinstance(expected, list):
        assert isinstance(actual, list), f"{path}: expected list, got {type(actual).__name__}"
        assert len(actual) == len(expected), f"{path}: length {len(actual)} != {len(expected)}"
        for index, (exp, act) in enumerate(zip(expected, actual, strict=True)):
            _assert_same(exp, act, f"{path}[{index}]")
    elif isinstance(expected, float):
        assert isinstance(actual, float), f"{path}: expected float, got {type(actual).__name__}"
        assert actual == pytest.approx(expected, rel=1e-12, abs=1e-12), path
    else:
        assert actual == expected, f"{path}: {actual!r} != {expected!r}"


class TestStarsGoldenSnapshot:
    def test_stars_payload_matches_snapshot(self) -> None:
        snapshot = json.loads(SNAPSHOT_PATH.read_text(encoding="utf-8"))
        result = StarsService().stars(**BIRTH)
        _assert_same(snapshot, result)

    def test_snapshot_covers_full_payload(self) -> None:
        snapshot = json.loads(SNAPSHOT_PATH.read_text(encoding="utf-8"))
        assert snapshot["count"] == 36
        assert len(snapshot["stars"]) == 36
        for section in ("meta", "birth", "stars"):
            assert section in snapshot
        assert snapshot["stars"][0]["magnitude"] <= snapshot["stars"][-1]["magnitude"]

    def test_snapshot_regeneration_is_idempotent(self) -> None:
        first = StarsService().stars(**BIRTH)
        second = StarsService().stars(**BIRTH)
        assert first == second
