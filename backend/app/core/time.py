"""
time.py — birth-moment value object and time-domain conversions.

Converts a civil birth instant (local date, local time, IANA timezone)
into a fully resolved astronomical instant: UTC datetime, Julian Day
(UT1 scale) and a Skyfield ``Time`` used for all ephemeris queries.

All arithmetic uses IEEE 754 float64 via NumPy.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from datetime import time as time_cls
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

import numpy as np
from skyfield.timelib import Time as SkyfieldTime

from app.core.ephemeris_loader import get_timescale
from app.exceptions import InvalidBirthDataError

# ═══════════════════════════════════════════════════════════════════════ #
# BirthMoment
# ═══════════════════════════════════════════════════════════════════════ #
# DE440 coverage window (NASA JPL): 1550-01-01 to 2650-01-25.
# ═══════════════════════════════════════════════════════════════════════ #


@dataclass(frozen=True)
class BirthMoment:
    """A fully-resolved astronomical instant derived from civil birth data.

    Attributes:
        date: Civil date ``YYYY-MM-DD``.
        time: Civil time ``HH:MM[:SS]``.
        timezone: IANA timezone name, e.g. ``Asia/Kolkata``.
        local: Aware local datetime of birth.
        utc: Aware UTC datetime of birth.
        jd_ut1: Julian Day number on the UT1 scale (float64).
        skyfield_time: Skyfield ``Time`` object for ephemeris queries.
    """

    date: str
    time: str
    timezone: str
    local: datetime
    utc: datetime
    jd_ut1: np.float64
    skyfield_time: SkyfieldTime


def build_birth_moment(date: str, time: str, timezone: str) -> BirthMoment:
    """Resolve civil birth data into a ``BirthMoment``.

    Raises:
        InvalidBirthDataError: on malformed date/time or unknown timezone.
    """
    try:
        year, month, day = (int(part) for part in date.split("-"))
        time_parts = time.split(":")
        hour = int(time_parts[0])
        minute = int(time_parts[1])
        second_str = time_parts[2] if len(time_parts) > 2 else "0"
        second_float = float(second_str)
        second = int(second_float)
        microsecond = int(round((second_float - second) * 1_000_000))
    except (ValueError, IndexError) as exc:
        raise InvalidBirthDataError(
            f"Invalid date/time format: date='{date}', time='{time}'",
            context={"field": "birth_time", "date": date, "time": time},
        ) from exc

    try:
        tz = ZoneInfo(timezone)
    except ZoneInfoNotFoundError as exc:
        raise InvalidBirthDataError(
            f"Unknown IANA timezone: '{timezone}'",
            context={"field": "timezone", "timezone": timezone},
        ) from exc

    try:
        local = datetime(
            year,
            month,
            day,
            hour,
            minute,
            second,
            microsecond,
            tzinfo=tz,
        )
    except ValueError as exc:
        raise InvalidBirthDataError(
            f"Date/time components out of range: date='{date}', time='{time}'",
            context={"field": "birth_time", "date": date, "time": time},
        ) from exc

    utc = local.astimezone(UTC)

    ts = get_timescale()
    sky_time = ts.utc(
        utc.year,
        utc.month,
        utc.day,
        utc.hour,
        utc.minute,
        np.float64(utc.second) + np.float64(utc.microsecond) / np.float64(1_000_000.0),
    )
    jd = np.float64(sky_time.ut1)

    return BirthMoment(
        date=date,
        time=time,
        timezone=timezone,
        local=local,
        utc=utc,
        jd_ut1=jd,
        skyfield_time=sky_time,
    )


def validate_jd_in_range(jd: np.float64) -> None:
    """Raise ``DateOutOfRangeError`` when ``jd`` falls outside DE440 coverage.

    References:
        Park et al. 2021, "The JPL Planetary and Lunar Ephemerides DE440
        and DE441" — coverage 1550-01-01 through 2650-01-25.
    """
    from app.exceptions import DateOutOfRangeError

    ts = get_timescale()
    jd_min = np.float64(ts.utc(1550, 1, 1).ut1)
    jd_max = np.float64(ts.utc(2650, 1, 25, 23, 59, 59).ut1)
    if not (jd_min <= jd <= jd_max):
        raise DateOutOfRangeError(
            f"Birth date outside DE440 ephemeris coverage "
            f"(1550-01-01 to 2650-01-25), got JD {float(jd):.5f}",
            context={"jd": float(jd)},
        )


def utc_datetime(year: int, month: int, day: int) -> datetime:
    """Return an aware midnight-UTC datetime for the given civil date."""
    return datetime(year, month, day, tzinfo=UTC)


def parse_time_string(value: str) -> time_cls:
    """Parse ``HH:MM[:SS]`` into a ``datetime.time`` (raises on bad input)."""
    try:
        parts = value.split(":")
        hour = int(parts[0])
        minute = int(parts[1])
        second = int(parts[2]) if len(parts) > 2 else 0
        return time_cls(hour, minute, second)
    except (ValueError, IndexError) as exc:
        raise InvalidBirthDataError(
            f"Invalid time format: '{value}' (expected HH:MM or HH:MM:SS)",
            context={"field": "time", "value": value},
        ) from exc
