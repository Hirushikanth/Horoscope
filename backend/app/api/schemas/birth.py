"""
birth.py — strict Pydantic v2 contract for birth data (requests).

``BirthRequest`` is the shared request body of every computation
endpoint. Structural validation (formats, coordinate bounds, option
enums) happens here so malformed input fails fast as a 422; semantic
validation (IANA timezone, DE440 date-range guard, real calendar dates)
happens when the request is resolved into a ``BirthMoment`` by
``app.core.time`` and surfaces as a typed domain error (400/422).

References:
    - docs/backend-v2-plan.md §1 (api/schemas), §3 (precision strategy)
    - docs/01-thirukanitha-jathakam-calculation.md §1 (birth inputs)
"""

from __future__ import annotations

from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

# ═══════════════════════════════════════════════════════════════════════ #
# Format patterns
# ═══════════════════════════════════════════════════════════════════════ #

#: ``YYYY-MM-DD`` — structural check only; calendar semantics are
#: validated downstream by ``build_birth_moment``.
DATE_PATTERN: str = r"^\d{4}-\d{2}-\d{2}$"

#: ``HH:MM`` or ``HH:MM:SS[.ffffff]``.
TIME_PATTERN: str = r"^\d{1,2}:\d{2}(:\d{2}(\.\d+)?)?$"


class BirthRequest(BaseModel):
    """Civil birth data shared by all v2 computation endpoints.

    Attributes:
        date: Civil birth date ``YYYY-MM-DD``.
        time: Civil birth time ``HH:MM`` or ``HH:MM:SS``.
        timezone: IANA timezone name (e.g. ``Asia/Kolkata``).
        latitude: Geographic latitude, degrees (north positive).
        longitude: Geographic longitude, degrees (east positive).
        node_convention: Lunar-node convention — ``mean`` (classical
            Thirukanitham default) or ``true`` (osculating).
    """

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
        str_min_length=1,
    )

    date: Annotated[str, Field(pattern=DATE_PATTERN)]
    time: Annotated[str, Field(pattern=TIME_PATTERN)]
    timezone: str
    latitude: Annotated[float, Field(ge=-90.0, le=90.0)]
    longitude: Annotated[float, Field(ge=-180.0, le=180.0)]
    node_convention: Literal["mean", "true"] = "mean"

    @field_validator("timezone")
    @classmethod
    def timezone_must_be_iana(cls, value: str) -> str:
        """Reject timezone strings that are not valid IANA zone names."""
        from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

        try:
            ZoneInfo(value)
        except ZoneInfoNotFoundError as exc:
            raise ValueError(f"unknown IANA timezone: '{value}'") from exc
        return value


class DashaOptions(BaseModel):
    """Optional tuning knobs for the Vimshottari dasha timeline.

    Attributes:
        depth: 1 = mahadashas, 2 = + antardashas, 3 = + pratyantardashas.
        year_length_days: Length of one dasha year — ``365.25`` (modern
            software default) or ``360`` (Tamil traditional).
        minimum_span_years: Generate mahadashas until the timeline spans
            at least this many years (120 = one full cycle).
    """

    depth: Literal[1, 2, 3] = 3
    year_length_days: float = Field(default=365.25, ge=1.0, le=1000.0)
    minimum_span_years: float = Field(default=120.0, ge=1.0, le=1000.0)

    @field_validator("year_length_days")
    @classmethod
    def year_length_days_supported(cls, value: float) -> float:
        """Only the two documented year lengths are supported."""
        if value not in (360.0, 365.25):
            raise ValueError("year_length_days must be 360.0 or 365.25")
        return value
