"""Shared test fixtures: memoised timescale and ephemeris."""

from __future__ import annotations

import pytest
from app.core.ephemeris_loader import get_ephemeris, get_timescale


@pytest.fixture(scope="session")
def ts():
    """Session-scoped Skyfield timescale (loads DE440 once)."""
    return get_timescale()


@pytest.fixture(scope="session")
def eph():
    """Session-scoped DE440 ephemeris wrapper."""
    return get_ephemeris()
