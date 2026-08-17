"""
stars.py — Pydantic v2 response contract for the stars endpoint.

``POST /api/v2/stars`` returns the proper-motion-corrected positions of
the embedded Hipparcos yogatara catalogue (the 27 junction stars of the
Nakshatras plus major navigation stars) at the birth instant.

References:
    - docs/backend-v2-plan.md §2 (``POST /api/v2/stars``)
    - docs/backend-v2-timeline.md Phase E (yogatara catalog, proper-motion corrected)
"""

from __future__ import annotations

from pydantic import BaseModel

from app.api.schemas.jathakam import BirthInfo, ComputationBadge, Trilingual

# ═══════════════════════════════════════════════════════════════════════ #
# Star entry
# ═══════════════════════════════════════════════════════════════════════ #


class StarInfo(BaseModel):
    """One catalogue star's position at the birth instant.

    The sidereal longitude is proper-motion corrected to the birth date;
    ``associated_nakshatra_index`` is the classical yogatara association
    (``None`` for non-yogatara stars) while ``nakshatra_index`` is where
    the star actually falls in the sidereal zodiac at that date.
    """

    hip_id: int
    name: str
    designation: str
    sanskrit_name: str | None
    associated_nakshatra_index: int | None
    associated_nakshatra: Trilingual | None
    magnitude: float
    ra_hours: float
    dec_degrees: float
    distance_light_years: float
    tropical_longitude_deg: float
    sidereal_longitude_deg: float
    ecliptic_latitude_deg: float
    rasi_index: int
    rasi: Trilingual
    nakshatra_index: int
    proper_motion_ra_mas_per_year: float
    proper_motion_dec_mas_per_year: float


# ═══════════════════════════════════════════════════════════════════════ #
# Endpoint response
# ═══════════════════════════════════════════════════════════════════════ #


class StarsResponse(BaseModel):
    """Yogatara catalogue positions at the birth moment."""

    meta: ComputationBadge
    birth: BirthInfo
    stars: list[StarInfo]
    count: int
