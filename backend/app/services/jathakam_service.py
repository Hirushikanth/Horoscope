"""
jathakam_service.py — assembles the complete Thirukanitha Jathakam.

Builds the flagship ``POST /api/v2/jathakam`` payload — panchangam,
lagna, all nine grahas (with D1 + D9 placements, dignity and
vargottama), whole-sign bhavas, the Vimshottari dasha balance and
timeline, and the Chevvai Dosham status — plus the focused dasha and
vargas payloads.

All values are computed at IEEE 754 float64 precision and converted to
native Python types only for the response.

References:
    - docs/01-thirukanitha-jathakam-calculation.md (complete jathakam)
    - docs/south-indian-horoscope.md §2.2, §3.7
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Callable
from typing import Any, Literal

import numpy as np

from app.astronomy.ascendant import get_sidereal_ascendant
from app.astronomy.ayanamsa import AyanamsaSystem, get_ayanamsa
from app.astronomy.positions import GrahaPosition, get_graha_positions
from app.config import Settings, get_settings
from app.core.cache import TTLCache
from app.core.serialization import sanitize_numpy
from app.core.time import BirthMoment
from app.services.common import (
    birth_info,
    computation_badge,
    jd_to_iso,
    rasi_record,
    resolve_birth,
    trilingual,
)
from app.services.panchangam_service import build_panchangam
from app.vedic.bhavas import get_bhava_of_longitude, get_whole_sign_bhavas, house_relations
from app.vedic.charts import Varga, get_navamsa_position, get_varga_position, is_vargottama
from app.vedic.dasha import (
    VIMSHOTTARI_YEARS,
    balance_years_to_days,
    vimshottari_balance,
    vimshottari_timeline,
)
from app.vedic.dignity import assess_dignity
from app.vedic.doshas import assess_chevvai_dosham
from app.vedic.nakshatra import get_nakshatra_index, get_nakshatra_pada_index
from app.vedic.rashi import get_rasi_index
from app.vedic.tables import GRAHA_NAME_BY_ID, NAKSHATRA_NAMES, Graha

# ═══════════════════════════════════════════════════════════════════════ #
# Entry builders
# ═══════════════════════════════════════════════════════════════════════ #


def _lagna_entry(lagna_sidereal: np.float64) -> dict[str, Any]:
    rasi_index = get_rasi_index(lagna_sidereal)
    navamsa = get_navamsa_position(lagna_sidereal)
    return {
        "sidereal_longitude_deg": float(lagna_sidereal),
        "rasi_index": rasi_index,
        "degree_in_sign_deg": float(lagna_sidereal % np.float64(30.0)),
        "rasi": rasi_record(rasi_index),
        "navamsa_rasi_index": navamsa.rasi_index,
        "navamsa_rasi": rasi_record(navamsa.rasi_index),
    }


def _graha_entry(name: str, position: GrahaPosition, lagna_rasi_index: int) -> dict[str, Any]:
    lon: np.float64 = position.sidereal_longitude
    rasi_index = get_rasi_index(lon)
    nakshatra_index = get_nakshatra_index(lon)
    dignity = assess_dignity(Graha(name), lon)
    navamsa = get_navamsa_position(lon)
    combustion = position.combustion

    return {
        "name": name,
        "names": trilingual(GRAHA_NAME_BY_ID[Graha(name)]),
        "tropical_longitude_deg": float(position.tropical_longitude),
        "sidereal_longitude_deg": float(lon),
        "rasi_index": rasi_index,
        "rasi": rasi_record(rasi_index),
        "degree_in_sign_deg": float(lon % np.float64(30.0)),
        "nakshatra_index": nakshatra_index,
        "nakshatra": trilingual(NAKSHATRA_NAMES[nakshatra_index]),
        "pada": get_nakshatra_pada_index(lon) + 1,
        "house_number": get_bhava_of_longitude(lagna_rasi_index, lon),
        "retrograde": position.retrograde,
        "combust": bool(combustion.get("combust", False)),
        "combustion_separation_deg": combustion.get("separation_deg"),
        "distance_au": float(position.distance_au),
        "dignity": {
            "dignity": dignity.dignity.value,
            "rasi_index": dignity.rasi_index,
            "degree_in_sign_deg": float(dignity.degree_in_sign),
            "distance_from_exaltation_deg": (
                None
                if dignity.distance_from_exaltation_deg is None
                else float(dignity.distance_from_exaltation_deg)
            ),
        },
        "navamsa_rasi_index": navamsa.rasi_index,
        "navamsa_rasi": rasi_record(navamsa.rasi_index),
        "vargottama": is_vargottama(lon),
    }


def _dasha_payload(
    birth: BirthMoment,
    moon_lon: np.float64,
    *,
    depth: int,
    year_length_days: float,
    minimum_span_years: float,
) -> dict[str, Any]:
    balance = vimshottari_balance(moon_lon)
    balance_entry = {
        "lord": balance.lord.value,
        "lord_years": float(VIMSHOTTARI_YEARS[balance.lord]),
        "balance_years": float(balance.balance_years),
        "balance_days": float(balance_years_to_days(balance.balance_years, year_length_days)),
        "fraction_remaining": float(balance.fraction_remaining),
        "janma_nakshatra_index": get_nakshatra_index(moon_lon),
    }
    periods = vimshottari_timeline(
        birth.jd_ut1,
        moon_lon,
        depth=depth,
        year_length_days=year_length_days,
        minimum_span_years=minimum_span_years,
    )
    period_entries = [
        {
            "graha": period.graha.value,
            "category": period.category,
            "years": float(period.years),
            "days": float(period.days),
            "start_jd": float(period.start_jd),
            "end_jd": float(period.end_jd),
            "start_utc": jd_to_iso(period.start_jd),
            "end_utc": jd_to_iso(period.end_jd),
        }
        for period in periods
    ]
    return {
        "year_length_days": float(year_length_days),
        "balance": balance_entry,
        "periods": period_entries,
    }


# ═══════════════════════════════════════════════════════════════════════ #
# JathakamService — orchestration with optional TTL caching
# ═══════════════════════════════════════════════════════════════════════ #


class JathakamService:
    """Computes jathakam payloads, caching deterministic results.

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

    def jathakam(
        self,
        date: str,
        time: str,
        timezone: str,
        latitude: float,
        longitude: float,
        *,
        node_convention: Literal["mean", "true"] = "mean",
    ) -> dict:
        """The complete Thirukanitha Jathakam (flagship payload)."""
        return self._cached(
            "jathakam",
            {
                "date": date,
                "time": time,
                "timezone": timezone,
                "latitude": latitude,
                "longitude": longitude,
                "node_convention": node_convention,
            },
            lambda: self._compute_jathakam(
                date,
                time,
                timezone,
                latitude,
                longitude,
                node_convention=node_convention,
            ),
        )

    def dasha(
        self,
        date: str,
        time: str,
        timezone: str,
        latitude: float,
        longitude: float,
        *,
        node_convention: Literal["mean", "true"] = "mean",
        depth: int = 3,
        year_length_days: float = 365.25,
        minimum_span_years: float = 120.0,
    ) -> dict:
        """The Vimshottari dasha timeline (MD/AD/PD) with birth balance."""
        return self._cached(
            "dasha",
            {
                "date": date,
                "time": time,
                "timezone": timezone,
                "latitude": latitude,
                "longitude": longitude,
                "node_convention": node_convention,
                "depth": depth,
                "year_length_days": year_length_days,
                "minimum_span_years": minimum_span_years,
            },
            lambda: self._compute_dasha(
                date,
                time,
                timezone,
                latitude,
                longitude,
                node_convention=node_convention,
                depth=depth,
                year_length_days=year_length_days,
                minimum_span_years=minimum_span_years,
            ),
        )

    def vargas(
        self,
        date: str,
        time: str,
        timezone: str,
        latitude: float,
        longitude: float,
        *,
        node_convention: Literal["mean", "true"] = "mean",
        vargas: list[str],
    ) -> dict:
        """Per-graha placements in the requested divisional charts."""
        return self._cached(
            "vargas",
            {
                "date": date,
                "time": time,
                "timezone": timezone,
                "latitude": latitude,
                "longitude": longitude,
                "node_convention": node_convention,
                "vargas": vargas,
            },
            lambda: self._compute_vargas(
                date,
                time,
                timezone,
                latitude,
                longitude,
                node_convention=node_convention,
                vargas=vargas,
            ),
        )

    # ────────────────────────── computation ─────────────────────────── #

    def _compute_jathakam(
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
        t = birth.skyfield_time
        ayanamsa = get_ayanamsa(t, AyanamsaSystem.LAHIRI)
        positions = get_graha_positions(t, node_convention=node_convention)
        lagna_sidereal = get_sidereal_ascendant(t, latitude, longitude, ayanamsa)
        lagna_rasi_index = get_rasi_index(lagna_sidereal)

        chevvai_dosham = assess_chevvai_dosham(
            positions["Mars"].sidereal_longitude,
            lagna_sidereal,
            positions["Moon"].sidereal_longitude,
            positions["Venus"].sidereal_longitude,
        )

        return sanitize_numpy(
            {
                "meta": computation_badge(ayanamsa, node_convention),
                "birth": birth_info(birth, latitude, longitude),
                "panchangam": build_panchangam(
                    birth, latitude, longitude, node_convention=node_convention
                ),
                "lagna": _lagna_entry(lagna_sidereal),
                "grahas": [
                    _graha_entry(name, position, lagna_rasi_index)
                    for name, position in positions.items()
                ],
                "bhavas": [
                    {
                        "house_number": bhava.house_number,
                        "rasi_index": bhava.rasi_index,
                        "rasi": rasi_record(bhava.rasi_index),
                        "lord": bhava.lord.value,
                        **house_relations(bhava.house_number),
                    }
                    for bhava in get_whole_sign_bhavas(lagna_rasi_index)
                ],
                "dasha": _dasha_payload(
                    birth,
                    positions["Moon"].sidereal_longitude,
                    depth=1,
                    year_length_days=365.25,
                    minimum_span_years=120.0,
                ),
                "chevvai_dosham": {
                    "present": chevvai_dosham.present,
                    "reference_count": chevvai_dosham.reference_count,
                    "houses_from_lagna": list(chevvai_dosham.houses_from_lagna),
                    "houses_from_moon": list(chevvai_dosham.houses_from_moon),
                    "houses_from_venus": list(chevvai_dosham.houses_from_venus),
                },
            }
        )

    def _compute_dasha(
        self,
        date: str,
        time: str,
        timezone: str,
        latitude: float,
        longitude: float,
        *,
        node_convention: Literal["mean", "true"],
        depth: int,
        year_length_days: float,
        minimum_span_years: float,
    ) -> dict:
        birth = resolve_birth(date, time, timezone)
        t = birth.skyfield_time
        ayanamsa = get_ayanamsa(t, AyanamsaSystem.LAHIRI)
        positions = get_graha_positions(t, node_convention=node_convention)
        moon_lon = positions["Moon"].sidereal_longitude
        return sanitize_numpy(
            {
                "meta": computation_badge(ayanamsa, node_convention),
                "birth": birth_info(birth, latitude, longitude),
                "dasha": _dasha_payload(
                    birth,
                    moon_lon,
                    depth=depth,
                    year_length_days=year_length_days,
                    minimum_span_years=minimum_span_years,
                ),
            }
        )

    def _compute_vargas(
        self,
        date: str,
        time: str,
        timezone: str,
        latitude: float,
        longitude: float,
        *,
        node_convention: Literal["mean", "true"],
        vargas: list[str],
    ) -> dict:
        birth = resolve_birth(date, time, timezone)
        t = birth.skyfield_time
        ayanamsa = get_ayanamsa(t, AyanamsaSystem.LAHIRI)
        positions = get_graha_positions(t, node_convention=node_convention)
        varga_enums = [Varga(value) for value in vargas]

        grahas = []
        for name, position in positions.items():
            placements = {
                varga.value: _varga_sign(position.sidereal_longitude, varga)
                for varga in varga_enums
            }
            grahas.append(
                {
                    "name": name,
                    "positions": placements,
                    "vargottama": is_vargottama(position.sidereal_longitude),
                }
            )

        return sanitize_numpy(
            {
                "meta": computation_badge(ayanamsa, node_convention),
                "birth": birth_info(birth, latitude, longitude),
                "grahas": grahas,
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


def _varga_sign(sidereal_longitude: np.float64, varga: Varga) -> dict[str, Any]:
    """Serialize a graha's placement in one divisional chart."""
    position = get_varga_position(sidereal_longitude, varga)
    return {
        "rasi_index": position.rasi_index,
        "rasi": rasi_record(position.rasi_index),
        "division_index": position.division_index,
    }
