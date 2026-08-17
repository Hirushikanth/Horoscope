"""
sun_time.py — local sunrise/sunset and the civil (Udaya) day.

The Tamil/Hindu civil day runs sunrise-to-sunrise, and the panchangam
"vara of the day" is anchored at the local sunrise. These times are
computed exactly at the birth location via Skyfield's almanac.

References:
    - docs/south-indian-horoscope.md, §3.6
"""

from __future__ import annotations

from datetime import UTC, datetime

import numpy as np
from skyfield import almanac
from skyfield.api import Topos
from skyfield.timelib import Time

from app.core.ephemeris_loader import get_ephemeris


def get_sunrise_sunset_utc(
    t: Time,
    latitude: float,
    longitude: float,
) -> tuple[datetime | None, datetime | None]:
    """Return the UTC sunrise and sunset of the UTC day containing ``t``.

    The window searched is the UTC calendar day of ``t`` (midnight to
    midnight UTC). For polar conditions where the Sun never rises or
    sets, both values are ``None``.

    Returns:
        ``(sunrise_utc, sunset_utc)`` — aware UTC datetimes, or ``(None, None)``.
    """
    ts = t.ts
    eph = get_ephemeris()
    topos = Topos(latitude_degrees=float(latitude), longitude_degrees=float(longitude))

    year, month, day = t.utc_datetime().year, t.utc_datetime().month, t.utc_datetime().day
    t0 = ts.utc(year, month, day)
    t1 = ts.utc(year, month, day + 1)

    f = almanac.sunrise_sunset(eph, topos)
    times, events = almanac.find_discrete(t0, t1, f)

    sunrise: datetime | None = None
    sunset: datetime | None = None
    for time_i, event in zip(times, events, strict=True):
        # find_discrete returns the state *after* each transition:
        # 1 → Sun risen (sunrise), 0 → Sun set (sunset).
        if event == 1 and sunrise is None:
            sunrise = time_i.utc_datetime().replace(tzinfo=UTC)
        elif event == 0 and sunset is None:
            sunset = time_i.utc_datetime().replace(tzinfo=UTC)

    return sunrise, sunset


def daylight_hours(
    t: Time,
    latitude: float,
    longitude: float,
) -> np.float64:
    """Daylight duration in hours for the UTC day containing ``t``."""
    sunrise, sunset = get_sunrise_sunset_utc(t, latitude, longitude)
    if sunrise is None or sunset is None:
        return np.float64(24.0) if sunrise is None and sunset is None else np.float64(0.0)
    delta = (sunset - sunrise).total_seconds()
    return np.float64(delta / 3600.0)
