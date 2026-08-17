"""
router.py — v2 API endpoints.

Phase A surface: operational endpoints (``/health``, ``/meta``).
Phase C surface: jathakam computation endpoints — the flagship
``POST /api/v2/jathakam`` plus the focused panchangam, dasha and vargas
endpoints.
Phase D surface: ``POST /api/v2/matching`` — the Kalyana Porutham
two-chart match.
Phase E surface: ``POST /api/v2/stars`` — yogatara catalogue positions
(proper-motion corrected).

The computation endpoints are synchronous (``def``), so FastAPI runs
them on the threadpool (CPU-bound ephemeris work never blocks the event
loop).
"""

from __future__ import annotations

import platform
from typing import Annotated

import numpy as np
import skyfield
from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field, field_validator

from app.api.deps import (
    get_jathakam_service,
    get_matching_service,
    get_panchangam_service,
    get_stars_service,
)
from app.api.schemas.birth import BirthRequest, DashaOptions
from app.api.schemas.jathakam import (
    DashaResponse,
    JathakamResponse,
    PanchangamResponse,
    VargasResponse,
)
from app.api.schemas.matching import MatchingResponse
from app.api.schemas.stars import StarsResponse
from app.astronomy.ayanamsa import AyanamsaSystem, get_ayanamsa
from app.config import get_settings
from app.core.ephemeris_loader import ephemeris_available, ephemeris_loaded, get_timescale
from app.core.serialization import sanitize_numpy
from app.exceptions import EphemerisUnavailableError
from app.services.jathakam_service import JathakamService
from app.services.matching_service import MatchingService
from app.services.panchangam_service import PanchangamService
from app.services.stars_service import StarsService

router = APIRouter(tags=["system"])


@router.get("/health")
async def health() -> dict:
    """Liveness/readiness probe — reports ephemeris availability."""
    cfg = get_settings()
    return {
        "status": "ok",
        "service": cfg.app_name,
        "version": cfg.version,
        "ephemeris": {
            "name": cfg.ephemeris_filename,
            "file_present": ephemeris_available(),
            "loaded": ephemeris_loaded(),
        },
    }


@router.get("/meta")
async def meta() -> dict:
    """Service metadata: ephemeris, ayanamsa, precision guarantees.

    The current Lahiri ayanamsa is computed live from the DE440
    ephemeris (requires the ephemeris to be loadable).
    """
    cfg = get_settings()
    if not ephemeris_available():
        raise EphemerisUnavailableError(
            f"JPL DE440 ephemeris not found at {cfg.ephemeris_path}.",
            context={"path": str(cfg.ephemeris_path)},
        )

    ts = get_timescale()
    now = ts.now()
    ayanamsa = get_ayanamsa(now, AyanamsaSystem.LAHIRI)

    return sanitize_numpy(
        {
            "name": cfg.app_name,
            "version": cfg.version,
            "ephemeris": {
                "name": cfg.ephemeris_filename,
                "source": "NASA JPL DE440",
                "coverage": {"start": "1550-01-01", "end": "2650-01-25"},
                "accuracy": "sub-arcsecond (Park et al. 2021)",
            },
            "precision": "IEEE 754 float64",
            "tradition": "Thirukanitham (Drik Ganita)",
            "ayanamsa": {
                "system": AyanamsaSystem.LAHIRI.value,
                "value_deg": np.float64(ayanamsa),
                "definition": "Chitra (Spica) fixed at 180° sidereal (Chitrapaksha)",
            },
            "node_convention": cfg.node_convention,
            "runtime": {
                "python": platform.python_version(),
                "skyfield": skyfield.__version__,
                "numpy": np.__version__,
            },
        }
    )


# ═══════════════════════════════════════════════════════════════════════ #
# Jathakam computation endpoints (Phase C)
# ═══════════════════════════════════════════════════════════════════════ #

jathakam_router = APIRouter(prefix="/jathakam", tags=["jathakam"])

#: The supported divisional chart ids (docs/01 §10).
VARGA_IDS: tuple[str, ...] = ("D1", "D9", "D10", "D12", "D30", "D60")


class DashaRequest(BirthRequest, DashaOptions):
    """Birth data plus Vimshottari dasha timeline options."""


class VargasRequest(BirthRequest):
    """Birth data plus the requested divisional charts."""

    vargas: list[str] = Field(default_factory=lambda: ["D9"], min_length=1)

    @field_validator("vargas")
    @classmethod
    def vargas_must_be_supported_unique(cls, value: list[str]) -> list[str]:
        """Reject unsupported ids or duplicate requests."""
        unsupported = [v for v in value if v not in VARGA_IDS]
        if unsupported:
            raise ValueError(
                f"unsupported varga id(s): {unsupported} (supported: {list(VARGA_IDS)})"
            )
        if len(value) != len(set(value)):
            raise ValueError("vargas must not contain duplicates")
        return value


@jathakam_router.post("", response_model=JathakamResponse)
def post_jathakam(
    payload: BirthRequest,
    service: Annotated[JathakamService, Depends(get_jathakam_service)],
) -> dict:
    """Complete Thirukanitha Jathakam — the flagship computation.

    Panchangam (5 angas), sidereal lagna, all nine grahas with D1+D9
    placements and dignity, whole-sign bhavas, Vimshottari mahadasha
    timeline and the Chevvai Dosham status.
    """
    return service.jathakam(
        date=payload.date,
        time=payload.time,
        timezone=payload.timezone,
        latitude=payload.latitude,
        longitude=payload.longitude,
        node_convention=payload.node_convention,
    )


@jathakam_router.post("/panchangam", response_model=PanchangamResponse)
def post_panchangam(
    payload: BirthRequest,
    service: Annotated[PanchangamService, Depends(get_panchangam_service)],
) -> dict:
    """Birth panchangam plus the daily almanac of the birth day.

    The five angas at the exact birth moment, then the Udaya-day
    sunrise/sunset and the Rahu Kalam, Yamagandam, Gulika and Abhijit
    windows in both UTC and local time.
    """
    return service.report(
        date=payload.date,
        time=payload.time,
        timezone=payload.timezone,
        latitude=payload.latitude,
        longitude=payload.longitude,
        node_convention=payload.node_convention,
    )


@jathakam_router.post("/dasha", response_model=DashaResponse)
def post_dasha(
    payload: DashaRequest,
    service: Annotated[JathakamService, Depends(get_jathakam_service)],
) -> dict:
    """Vimshottari dasha timeline with the balance of the first dasa at birth.

    ``depth``: 1 = mahadashas, 2 = + antardashas, 3 = + pratyantardashas.
    ``year_length_days``: 365.25 (modern default) or 360 (Tamil traditional).
    """
    return service.dasha(
        date=payload.date,
        time=payload.time,
        timezone=payload.timezone,
        latitude=payload.latitude,
        longitude=payload.longitude,
        node_convention=payload.node_convention,
        depth=payload.depth,
        year_length_days=payload.year_length_days,
        minimum_span_years=payload.minimum_span_years,
    )


@jathakam_router.post("/vargas", response_model=VargasResponse)
def post_vargas(
    payload: VargasRequest,
    service: Annotated[JathakamService, Depends(get_jathakam_service)],
) -> dict:
    """Per-graha placements in the requested divisional charts (D1–D60)."""
    return service.vargas(
        date=payload.date,
        time=payload.time,
        timezone=payload.timezone,
        latitude=payload.latitude,
        longitude=payload.longitude,
        node_convention=payload.node_convention,
        vargas=payload.vargas,
    )


router.include_router(jathakam_router)


# ═══════════════════════════════════════════════════════════════════════ #
# Kalyana Porutham matching endpoint (Phase D)
# ═══════════════════════════════════════════════════════════════════════ #

matching_router = APIRouter(prefix="/matching", tags=["matching"])


class MatchingRequest(BaseModel):
    """Two birth data sets — the bride (பெண்) and the groom (ஆண்).

    References:
        docs/02-kalyana-porutham-matching.md, §0
    """

    model_config = {"extra": "forbid"}

    bride: BirthRequest
    groom: BirthRequest


@matching_router.post("", response_model=MatchingResponse)
def post_matching(
    payload: MatchingRequest,
    service: Annotated[MatchingService, Depends(get_matching_service)],
) -> dict:
    """Kalyana Porutham — the complete two-chart marriage match.

    All eleven checks (Dina, Gana, Mahendra, Stree Deergha, Yoni, Rasi,
    Rasi Athipathi, Vashya, Rajju, Vedha + Nadi), the 10-point score,
    the overall verdict with Rajju/Vedha gates and non-negotiable
    poruthams, and the Chevvai Dosham cross-check.
    """
    return service.match(
        bride=payload.bride.model_dump(),
        groom=payload.groom.model_dump(),
        node_convention=payload.bride.node_convention,
    )


router.include_router(matching_router)


# ═══════════════════════════════════════════════════════════════════════ #
# Yogatara stars endpoint (Phase E)
# ═══════════════════════════════════════════════════════════════════════ #

stars_router = APIRouter(prefix="/stars", tags=["stars"])


@stars_router.post("", response_model=StarsResponse)
def post_stars(
    payload: BirthRequest,
    service: Annotated[StarsService, Depends(get_stars_service)],
) -> dict:
    """Yogatara catalogue positions at the birth moment.

    The 27 junction stars of the Nakshatras plus major navigation stars,
    proper-motion corrected to the birth date, in tropical and sidereal
    (Lahiri) ecliptic coordinates with sign and nakshatra placement.
    """
    return service.stars(
        date=payload.date,
        time=payload.time,
        timezone=payload.timezone,
        latitude=payload.latitude,
        longitude=payload.longitude,
        node_convention=payload.node_convention,
    )


router.include_router(stars_router)
