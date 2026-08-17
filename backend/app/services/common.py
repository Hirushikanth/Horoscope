"""
common.py — helpers shared by the service layer.

Response-shaping utilities (trilingual name serialization, the
"Thirukanitha badge", birth echo) and the birth-resolution guard used
by every computation endpoint.
"""

from __future__ import annotations

from typing import Any, Literal

import numpy as np

from app.astronomy.ayanamsa import AyanamsaSystem
from app.config import get_settings
from app.core.ephemeris_loader import get_timescale
from app.core.time import BirthMoment, build_birth_moment, validate_jd_in_range
from app.vedic.tables import RASI_BY_INDEX, RASI_NAME_BY_ID, TrilingualName

# ═══════════════════════════════════════════════════════════════════════ #
# Name records and birth resolution
# ═══════════════════════════════════════════════════════════════════════ #


def trilingual(record: TrilingualName) -> dict[str, str | None]:
    """Serialize a trilingual name record to a response dict."""
    return {
        "english": record.english,
        "sanskrit": record.sanskrit,
        "tamil": record.tamil,
        "sinhala": record.sinhala,
    }


def rasi_record(rasi_index: int) -> dict[str, str | None]:
    """Trilingual record of the rasi at 0-based ``rasi_index``."""
    return trilingual(RASI_NAME_BY_ID[RASI_BY_INDEX[rasi_index]])


def resolve_birth(date: str, time: str, timezone: str) -> BirthMoment:
    """Resolve civil birth data, guarding the DE440 coverage window.

    Raises:
        InvalidBirthDataError: malformed date/time or unknown timezone.
        DateOutOfRangeError: date outside DE440 coverage (1550–2650).
    """
    birth = build_birth_moment(date, time, timezone)
    validate_jd_in_range(birth.jd_ut1)
    return birth


def birth_info(birth: BirthMoment, latitude: float, longitude: float) -> dict[str, Any]:
    """Echo of the resolved birth input plus the astronomical instant."""
    return {
        "date": birth.date,
        "time": birth.time,
        "timezone": birth.timezone,
        "latitude": latitude,
        "longitude": longitude,
        "local_datetime": birth.local.isoformat(),
        "utc_datetime": birth.utc.isoformat(),
        "jd_ut1": float(birth.jd_ut1),
    }


def jd_to_iso(jd: np.float64) -> str:
    """Convert a UT1 Julian day to an ISO 8601 UTC timestamp."""
    return get_timescale().ut1(jd).utc_iso()


def computation_badge(
    ayanamsa: np.float64, node_convention: Literal["mean", "true"]
) -> dict[str, Any]:
    """The "Thirukanitha badge" — self-description of every computation.

    Parameters:
        ayanamsa: Ayanamsa value used for the computation (degrees).
        node_convention: Node convention used (``mean`` or ``true``).
    """
    cfg = get_settings()
    return {
        "version": cfg.version,
        "tradition": "Thirukanitham (Drik Ganita)",
        "precision": "IEEE 754 float64",
        "ephemeris": {
            "name": cfg.ephemeris_filename,
            "source": "NASA JPL DE440",
            "coverage": {"start": "1550-01-01", "end": "2650-01-25"},
            "accuracy": "sub-arcsecond (Park et al. 2021)",
        },
        "ayanamsa": {
            "system": AyanamsaSystem.LAHIRI.value,
            "value_deg": float(ayanamsa),
            "definition": "Chitra (Spica) fixed at 180° sidereal (Chitrapaksha)",
        },
        "node_convention": node_convention,
    }
