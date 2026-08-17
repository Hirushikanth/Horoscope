"""
panchangam_service.py — birth panchangam and the daily almanac.

Assembles the five angas (Thithi, Vaaram, Nakshatram, Yogam, Karanam)
at the exact birth moment and the almanac of the birth day (sunrise,
sunset, Rahu Kalam, Yamagandam, Gulika, Abhijit) into the
``POST /api/v2/jathakam/panchangam`` payload.

References:
    - docs/01-thirukanitha-jathakam-calculation.md   §5 (five angas)
    - docs/south-indian-horoscope.md                 §3.6 (almanac)
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Callable
from datetime import datetime
from typing import Any, Literal
from zoneinfo import ZoneInfo

import numpy as np

from app.astronomy.ayanamsa import AyanamsaSystem, get_ayanamsa
from app.astronomy.positions import get_graha_positions
from app.config import Settings, get_settings
from app.core.cache import TTLCache
from app.core.serialization import sanitize_numpy
from app.core.time import BirthMoment
from app.services.common import birth_info, computation_badge, resolve_birth, trilingual
from app.vedic.nakshatra import get_nakshatra_index, get_nakshatra_lord, get_nakshatra_pada_index
from app.vedic.panchangam import (
    TimeWindow,
    get_daily_almanac,
    get_karana_id,
    get_karana_sequence_index,
    get_tithi_index,
    get_tithi_paksha,
    get_vara_index,
    get_yoga_index,
)
from app.vedic.tables import (
    NAKSHATRA_NAMES,
    VARA_NAMES,
    get_karana_name,
    get_tithi_name,
    get_yoga_name,
)

# ═══════════════════════════════════════════════════════════════════════ #
# Birth panchangam — the five angas
# ═══════════════════════════════════════════════════════════════════════ #


def build_panchangam(
    birth: BirthMoment,
    latitude: float,
    longitude: float,
    node_convention: Literal["mean", "true"] = "mean",
) -> dict:
    """The five angas at the exact birth moment (all from Sun/Moon).

    Parameters:
        birth: Resolved birth moment.
        latitude: Geographic latitude, degrees.
        longitude: Geographic longitude, degrees.
        node_convention: Node convention — only affects the position
            computation, not the angas themselves.

    Returns:
        A dict with ``tithi``, ``vara``, ``nakshatra``, ``yoga`` and
        ``karana`` entries (indices + trilingual names).
    """
    t = birth.skyfield_time
    positions = get_graha_positions(t, node_convention=node_convention)
    sun_lon: np.float64 = positions["Sun"].sidereal_longitude
    moon_lon: np.float64 = positions["Moon"].sidereal_longitude

    tithi_index = get_tithi_index(sun_lon, moon_lon)
    nakshatra_index = get_nakshatra_index(moon_lon)
    yoga_index = get_yoga_index(sun_lon, moon_lon)
    karana_index = get_karana_id(get_karana_sequence_index(sun_lon, moon_lon))
    vara_index = get_vara_index(t, latitude, longitude, birth.timezone)

    return {
        "tithi": {
            "index": tithi_index,
            "number": tithi_index + 1,
            "paksha": get_tithi_paksha(tithi_index).value,
            "name": trilingual(get_tithi_name(tithi_index)),
        },
        "vara": {
            "index": vara_index,
            "name": trilingual(VARA_NAMES[vara_index]),
        },
        "nakshatra": {
            "index": nakshatra_index,
            "pada": get_nakshatra_pada_index(moon_lon) + 1,
            "lord": get_nakshatra_lord(nakshatra_index).value,
            "name": trilingual(NAKSHATRA_NAMES[nakshatra_index]),
        },
        "yoga": {
            "index": yoga_index,
            "name": trilingual(get_yoga_name(yoga_index)),
        },
        "karana": {
            "index": karana_index,
            "name": trilingual(get_karana_name(karana_index)),
        },
    }


# ═══════════════════════════════════════════════════════════════════════ #
# Daily almanac of the birth day
# ═══════════════════════════════════════════════════════════════════════ #


def _iso_utc(value: datetime | None) -> str | None:
    """Format an aware UTC datetime as ISO 8601 (or ``None``)."""
    return None if value is None else value.isoformat()


def _local_iso(value: datetime | None, timezone: str) -> str | None:
    """Format an aware UTC datetime in the birth timezone (or ``None``)."""
    if value is None:
        return None
    return value.astimezone(ZoneInfo(timezone)).isoformat()


def _window(value: TimeWindow | None, timezone: str) -> dict | None:
    """Serialize an almanac window in both UTC and local time."""
    if value is None:
        return None
    return {
        "start_local": _local_iso(value.start_utc, timezone),
        "end_local": _local_iso(value.end_utc, timezone),
        "start_utc": _iso_utc(value.start_utc),
        "end_utc": _iso_utc(value.end_utc),
    }


def build_almanac(birth: BirthMoment, latitude: float, longitude: float) -> dict:
    """The full daily almanac of the Udaya day containing the birth instant.

    Returns:
        A dict matching ``DailyAlmanac`` (windows ``None`` under polar
        conditions).
    """
    t = birth.skyfield_time
    almanac = get_daily_almanac(t, latitude, longitude, birth.timezone)
    vara_index = almanac["vara_index"]

    report: dict = {
        "available": bool(almanac["available"]),
        "vara": {
            "index": vara_index,
            "name": trilingual(VARA_NAMES[vara_index]),
        },
        "sunrise_utc": None,
        "sunrise_local": None,
        "sunset_utc": None,
        "sunset_local": None,
        "next_sunrise_utc": None,
        "next_sunrise_local": None,
        "rahu_kalam": None,
        "yamagandam": None,
        "gulika": None,
        "abhijit": None,
    }
    if not almanac["available"]:
        return report

    timezone = birth.timezone
    report.update(
        {
            "sunrise_utc": _iso_utc(almanac["sunrise_utc"]),
            "sunrise_local": _local_iso(almanac["sunrise_utc"], timezone),
            "sunset_utc": _iso_utc(almanac["sunset_utc"]),
            "sunset_local": _local_iso(almanac["sunset_utc"], timezone),
            "next_sunrise_utc": _iso_utc(almanac["next_sunrise_utc"]),
            "next_sunrise_local": _local_iso(almanac["next_sunrise_utc"], timezone),
            "rahu_kalam": _window(almanac["rahu_kalam"], timezone),
            "yamagandam": _window(almanac["yamagandam"], timezone),
            "gulika": _window(almanac["gulika"], timezone),
            "abhijit": _window(almanac["abhijit"], timezone),
        }
    )
    return report


class PanchangamService:
    """Assembles the ``POST /api/v2/jathakam/panchangam`` payload.

    Parameters:
        settings: Application settings (defaults to the singleton).
        cache: Optional TTL cache keyed by request fingerprint.
    """

    def __init__(
        self,
        settings: Settings | None = None,
        cache: TTLCache | None = None,
    ) -> None:
        self._settings = settings or get_settings()
        self._cache = cache

    def report(
        self,
        date: str,
        time: str,
        timezone: str,
        latitude: float,
        longitude: float,
        *,
        node_convention: Literal["mean", "true"] = "mean",
    ) -> dict:
        """Birth panchangam plus the daily almanac of the birth day."""
        params: dict[str, Any] = {
            "date": date,
            "time": time,
            "timezone": timezone,
            "latitude": latitude,
            "longitude": longitude,
            "node_convention": node_convention,
        }
        return self._cached(
            "panchangam",
            params,
            lambda: self._compute_report(
                date,
                time,
                timezone,
                latitude,
                longitude,
                node_convention=node_convention,
            ),
        )

    def _compute_report(
        self,
        date: str,
        time: str,
        timezone: str,
        latitude: float,
        longitude: float,
        *,
        node_convention: Literal["mean", "true"],
    ) -> dict:
        birth = resolve_birth(date, time, timezone)
        ayanamsa = get_ayanamsa(birth.skyfield_time, AyanamsaSystem.LAHIRI)
        return sanitize_numpy(
            {
                "meta": computation_badge(ayanamsa, node_convention),
                "birth": birth_info(birth, latitude, longitude),
                "panchangam": build_panchangam(
                    birth, latitude, longitude, node_convention=node_convention
                ),
                "almanac": build_almanac(birth, latitude, longitude),
            }
        )

    # ─────────────────────────── helpers ────────────────────────────── #

    def _cached(self, kind: str, params: dict[str, Any], compute: Callable[[], dict]) -> dict:
        if self._cache is None:
            return compute()
        return self._cache.get_or_compute(self._fingerprint(kind, params), compute)

    @staticmethod
    def _fingerprint(kind: str, params: dict[str, Any]) -> str:
        blob = json.dumps({"kind": kind, **params}, sort_keys=True, default=str)
        return hashlib.sha256(blob.encode("utf-8")).hexdigest()
