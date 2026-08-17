"""
stars_service.py — yogatara catalogue positions (proper-motion corrected).

Assembles the ``POST /api/v2/stars`` payload: for each catalogue star the
apparent equatorial and ecliptic coordinates at the birth instant,
sidereal longitude in the Lahiri frame, the sign it currently occupies,
and the classical yogatara association.

Results are deterministic for identical inputs and cached with the
shared TTL cache.

References:
    - docs/backend-v2-timeline.md, Phase E (Day 1: stars endpoint)
    - docs/backend-v2-plan.md §2 (``POST /api/v2/stars``)
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Callable
from typing import Any, Literal

import numpy as np

from app.astronomy.ayanamsa import AyanamsaSystem, get_ayanamsa
from app.astronomy.stars import STAR_CATALOG, StarPosition, get_star_positions, nakshatra_index_of
from app.config import Settings, get_settings
from app.core.cache import TTLCache
from app.core.serialization import sanitize_numpy
from app.services.common import (
    birth_info,
    computation_badge,
    rasi_record,
    resolve_birth,
    trilingual,
)
from app.vedic.rashi import get_rasi_index
from app.vedic.tables import NAKSHATRA_NAMES

# ═══════════════════════════════════════════════════════════════════════ #
# Entry builder
# ═══════════════════════════════════════════════════════════════════════ #


def _star_entry(position: StarPosition) -> dict[str, Any]:
    entry = position.entry
    associated_index = entry.associated_nakshatra_index
    sidereal: np.float64 = position.sidereal_longitude
    return {
        "hip_id": entry.hip_id,
        "name": entry.name,
        "designation": entry.designation,
        "sanskrit_name": entry.sanskrit_name,
        "associated_nakshatra_index": associated_index,
        "associated_nakshatra": (
            None if associated_index is None else trilingual(NAKSHATRA_NAMES[associated_index])
        ),
        "magnitude": float(entry.magnitude),
        "ra_hours": float(position.ra_hours),
        "dec_degrees": float(position.dec_degrees),
        "distance_light_years": float(position.distance_light_years),
        "tropical_longitude_deg": float(position.tropical_longitude),
        "sidereal_longitude_deg": float(sidereal),
        "ecliptic_latitude_deg": float(position.ecliptic_latitude),
        "rasi_index": get_rasi_index(sidereal),
        "rasi": rasi_record(get_rasi_index(sidereal)),
        "nakshatra_index": nakshatra_index_of(sidereal),
        "proper_motion_ra_mas_per_year": float(entry.ra_proper_motion),
        "proper_motion_dec_mas_per_year": float(entry.dec_proper_motion),
    }


# ═══════════════════════════════════════════════════════════════════════ #
# StarsService — orchestration with optional TTL caching
# ═══════════════════════════════════════════════════════════════════════ #


class StarsService:
    """Computes yogatara positions, caching deterministic results.

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

    # ─────────────────────────── public API ─────────────────────────── #

    def stars(
        self,
        date: str,
        time: str,
        timezone: str,
        latitude: float,
        longitude: float,
        *,
        node_convention: Literal["mean", "true"] = "mean",
    ) -> dict:
        """Yogatara catalogue positions at the birth moment."""
        params: dict[str, Any] = {
            "date": date,
            "time": time,
            "timezone": timezone,
            "latitude": latitude,
            "longitude": longitude,
            "node_convention": node_convention,
        }
        return self._cached(
            "stars",
            params,
            lambda: self._compute_stars(
                date,
                time,
                timezone,
                latitude,
                longitude,
                node_convention=node_convention,
            ),
        )

    # ────────────────────────── computation ─────────────────────────── #

    def _compute_stars(
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
        positions = get_star_positions(
            birth.skyfield_time, ayanamsa, node_convention=node_convention
        )
        return sanitize_numpy(
            {
                "meta": computation_badge(ayanamsa, node_convention),
                "birth": birth_info(birth, latitude, longitude),
                "stars": [_star_entry(position) for position in positions],
                "count": len(STAR_CATALOG),
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
