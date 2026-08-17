"""
matching_service.py — the two-chart Kalyana Porutham pipeline.

Computes both partners' jathakam essentials (Janma Nakshatra + Pada,
Chandra Rasi, Moon degree in sign, Chevvai Dosham status) from their
birth data, runs the eleven porutham checks from ``app.matching``, scores
the ten and produces the overall verdict with its gate and
non-negotiable reasons, plus the Chevvai Dosham cross-check.

All values are computed at IEEE 754 float64 precision and converted to
native Python types only for the response.

References:
    - docs/02-kalyana-porutham-matching.md (complete porutham workflow)
    - docs/01-thirukanitha-jathakam-calculation.md §12 (Chevvai Dosham)
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Callable
from typing import Any, Literal

import numpy as np

from app.astronomy.ascendant import get_sidereal_ascendant
from app.astronomy.ayanamsa import AyanamsaSystem, get_ayanamsa
from app.astronomy.positions import get_graha_positions
from app.config import Settings, get_settings
from app.core.cache import TTLCache
from app.core.serialization import sanitize_numpy
from app.core.time import BirthMoment
from app.matching.poruthams import (
    PORUTHAM_GOVERNS,
    PORUTHAM_NAMES,
    MatchingInput,
    compute_all_poruthams,
)
from app.matching.scoring import assess_verdict, score_reports
from app.services.common import (
    birth_info,
    computation_badge,
    rasi_record,
    resolve_birth,
    trilingual,
)
from app.vedic.doshas import assess_chevvai_dosham
from app.vedic.nakshatra import get_nakshatra_index, get_nakshatra_pada_index
from app.vedic.rashi import get_rasi_index
from app.vedic.tables import NAKSHATRA_NAMES

# ═══════════════════════════════════════════════════════════════════════ #
# MatchingService — orchestration with optional TTL caching
# ═══════════════════════════════════════════════════════════════════════ #


class MatchingService:
    """Computes Kalyana Porutham matches, caching deterministic results.

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

    def match(
        self,
        bride: dict[str, Any],
        groom: dict[str, Any],
        *,
        node_convention: Literal["mean", "true"] = "mean",
    ) -> dict:
        """The complete Kalyana Porutham match (flagship payload)."""
        params = {
            "bride": _fingerprint_birth(bride),
            "groom": _fingerprint_birth(groom),
            "node_convention": node_convention,
        }
        return self._cached(
            "matching",
            params,
            lambda: self._compute_match(bride, groom, node_convention=node_convention),
        )

    # ────────────────────────── computation ─────────────────────────── #

    def _compute_match(
        self,
        bride: dict[str, Any],
        groom: dict[str, Any],
        *,
        node_convention: Literal["mean", "true"],
    ) -> dict:
        bride_birth = resolve_birth(bride["date"], bride["time"], bride["timezone"])
        groom_birth = resolve_birth(groom["date"], groom["time"], groom["timezone"])

        bride_input, bride_brief = self._partner_brief(
            bride_birth, bride["latitude"], bride["longitude"], node_convention
        )
        groom_input, groom_brief = self._partner_brief(
            groom_birth, groom["latitude"], groom["longitude"], node_convention
        )

        reports = compute_all_poruthams(bride_input, groom_input)
        score = score_reports(reports)
        verdict = assess_verdict(reports)

        porutham_entries = [
            {
                "id": report.id,
                "name": trilingual(PORUTHAM_NAMES[report.id]),
                "governs": PORUTHAM_GOVERNS[report.id],
                "result": report.result.value,
                "score": float(report.result.score),
                "in_total": report.in_total,
                "detail": report.detail,
                "notes": list(report.notes),
            }
            for report in (
                reports["dina"],
                reports["gana"],
                reports["mahendra"],
                reports["stree_deergha"],
                reports["yoni"],
                reports["rasi"],
                reports["rasi_athipathi"],
                reports["vashya"],
                reports["rajju"],
                reports["vedha"],
                reports["nadi"],
            )
        ]

        ayanamsa = get_ayanamsa(bride_birth.skyfield_time, AyanamsaSystem.LAHIRI)

        return sanitize_numpy(
            {
                "meta": computation_badge(ayanamsa, node_convention),
                "tradition": "Kalyana Porutham (Tamil convention)",
                "bride": bride_brief,
                "groom": groom_brief,
                "poruthams": porutham_entries,
                "score": {
                    "total": float(score.total),
                    "out_of": score.out_of,
                    "uthamam_count": score.uthamam_count,
                    "madhyamam_count": score.madhyamam_count,
                    "athamam_count": score.athamam_count,
                },
                "verdict": {
                    "verdict": verdict.verdict.value,
                    "band": verdict.band,
                    "gates": verdict.gates,
                    "non_negotiables": verdict.non_negotiables,
                    "gate_overridden": verdict.gate_overridden,
                    "reasons": list(verdict.reasons),
                },
                "chevvai_cross_check": self._chevvai_cross_check(bride_input, groom_input),
            }
        )

    # ─────────────────────────── helpers ────────────────────────────── #

    def _partner_brief(
        self,
        birth: BirthMoment,
        latitude: float,
        longitude: float,
        node_convention: Literal["mean", "true"],
    ) -> tuple[MatchingInput, dict[str, Any]]:
        """Compute one partner's matching inputs and response brief."""
        t = birth.skyfield_time
        positions = get_graha_positions(t, node_convention=node_convention)
        moon_lon: np.float64 = positions["Moon"].sidereal_longitude
        lagna_sidereal = get_sidereal_ascendant(
            t, latitude, longitude, get_ayanamsa(t, AyanamsaSystem.LAHIRI)
        )

        nakshatra_index = get_nakshatra_index(moon_lon)
        rasi_index = get_rasi_index(moon_lon)
        degree_in_sign = moon_lon % np.float64(30.0)

        chevvai = assess_chevvai_dosham(
            positions["Mars"].sidereal_longitude,
            lagna_sidereal,
            moon_lon,
            positions["Venus"].sidereal_longitude,
        )

        matching_input = MatchingInput(
            nakshatra_index=nakshatra_index,
            pada=get_nakshatra_pada_index(moon_lon) + 1,
            rasi_index=rasi_index,
            moon_degree_in_sign=degree_in_sign,
            chevvai_dosham=chevvai.present,
        )

        brief = {
            "birth": birth_info(birth, latitude, longitude),
            "nakshatra_index": nakshatra_index,
            "pada": matching_input.pada,
            "nakshatra": trilingual(NAKSHATRA_NAMES[nakshatra_index]),
            "rasi_index": rasi_index,
            "rasi": rasi_record(rasi_index),
            "moon_degree_in_sign_deg": float(degree_in_sign),
            "chevvai_dosham": chevvai.present,
        }
        return matching_input, brief

    @staticmethod
    def _chevvai_cross_check(bride: MatchingInput, groom: MatchingInput) -> dict[str, Any]:
        """The Chevvai Dosham cross-check — separate from the 10 points.

        Compatible when both partners share the same status (both have
        it or neither does); one-sided presence needs closer study.

        References:
            docs/02-kalyana-porutham-matching.md — "Cross-check"
        """
        both = bride.chevvai_dosham and groom.chevvai_dosham
        neither = not bride.chevvai_dosham and not groom.chevvai_dosham
        compatible = both or neither
        if both:
            note = "Both partners have Chevvai Dosham — compatible."
        elif neither:
            note = "Neither partner has Chevvai Dosham — compatible."
        else:
            note = (
                "Only one partner has Chevvai Dosham — needs closer study; "
                "remedies (parihaaram) are often recommended."
            )
        return {
            "bride_dosham": bride.chevvai_dosham,
            "groom_dosham": groom.chevvai_dosham,
            "compatible": compatible,
            "note": note,
        }

    def _cached(self, kind: str, params: dict[str, Any], compute: Callable[[], dict]) -> dict:
        if self._cache is None:
            return compute()
        return self._cache.get_or_compute(self._fingerprint(kind, params), compute)

    @staticmethod
    def _fingerprint(kind: str, params: dict[str, Any]) -> str:
        blob = json.dumps({"kind": kind, **params}, sort_keys=True, default=str)
        return hashlib.sha256(blob.encode("utf-8")).hexdigest()


def _fingerprint_birth(birth: dict[str, Any]) -> dict[str, Any]:
    """Canonical birth data for cache fingerprinting."""
    return {
        "date": birth["date"],
        "time": birth["time"],
        "timezone": birth["timezone"],
        "latitude": birth["latitude"],
        "longitude": birth["longitude"],
    }
