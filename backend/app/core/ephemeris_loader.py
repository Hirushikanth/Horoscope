"""
ephemeris_loader.py — thread-safe NASA JPL DE440 loader.

Loads the DE440 planetary ephemeris (.bsp) once, lazily, guarded by a
lock so concurrent first requests do not double-load. The Skyfield
timescale uses its bundled builtin Delta-T tables (no network).

References:
    Park et al. 2021, "The JPL Planetary and Lunar Ephemerides DE440 and
    DE441", Astronomical Journal 161, 105.
"""

from __future__ import annotations

import logging
import threading
from pathlib import Path
from typing import Any

from skyfield.jpllib import SpiceKernel
from skyfield.timelib import Timescale
from skyfield.vectorlib import VectorSum

from app.config import get_settings
from app.exceptions import EphemerisUnavailableError

logger = logging.getLogger(__name__)

_lock = threading.Lock()
_state: dict[str, Any] = {"ts": None, "eph": None, "earth": None}


def _resolve_ephemeris_path() -> Path:
    settings = get_settings()
    if not settings.ephemeris_path.exists():
        if settings.auto_download_ephemeris:
            return settings.ephemeris_path  # Loader will download it
        raise EphemerisUnavailableError(
            f"JPL DE440 ephemeris not found at {settings.ephemeris_path}. "
            f"Place de440.bsp in the data directory or set "
            f"JYOTISHA_AUTO_DOWNLOAD_EPHEMERIS=true.",
            context={"path": str(settings.ephemeris_path)},
        )
    return settings.ephemeris_path


def load_ephemeris() -> tuple[Timescale, SpiceKernel, VectorSum]:
    """Load (timescale, ephemeris, earth) — thread-safe, memoised.

    Returns:
        A tuple ``(ts, eph, earth)`` where ``ts`` is the Skyfield timescale,
        ``eph`` the DE440 file wrapper and ``earth`` the Earth object.
    """
    global _state
    if _state["ts"] is not None and _state["eph"] is not None:
        return _state["ts"], _state["eph"], _state["earth"]

    with _lock:
        if _state["ts"] is not None and _state["eph"] is not None:
            return _state["ts"], _state["eph"], _state["earth"]

        _resolve_ephemeris_path()
        settings = get_settings()
        settings.data_dir.mkdir(parents=True, exist_ok=True)

        from skyfield.api import Loader

        loader = Loader(str(settings.data_dir))
        ts = loader.timescale(builtin=True)
        eph = loader(str(settings.ephemeris_filename))
        earth = eph["earth"]

        _state.update(ts=ts, eph=eph, earth=earth)
        logger.info("ephemeris loaded: %s", settings.ephemeris_filename)
        return ts, eph, earth


def get_timescale() -> Timescale:
    """Return the memoised Skyfield timescale."""
    ts, _, _ = load_ephemeris()
    return ts


def get_ephemeris() -> SpiceKernel:
    """Return the memoised DE440 ephemeris wrapper."""
    _, eph, _ = load_ephemeris()
    return eph


def get_earth() -> VectorSum:
    """Return the memoised Earth object."""
    _, _, earth = load_ephemeris()
    return earth


def ephemeris_available() -> bool:
    """True when the ephemeris file exists on disk (no load attempt)."""
    settings = get_settings()
    return settings.ephemeris_path.exists()


def ephemeris_loaded() -> bool:
    """True when the ephemeris has been loaded into memory."""
    return _state["eph"] is not None
