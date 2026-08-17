"""
panchangam.py — the five angas (Panchangam) and the daily almanac.

The five angas — Thithi, Vaaram, Nakshatram, Yogam, Karanam — are
computed for the exact birth moment from the Sun's and Moon's sidereal
longitudes, exactly as a Thirukanitham jathakam records them.

The Tamil civil day runs **sunrise to sunrise** (Udaya convention), so
the vara is anchored at the local sunrise. The daily almanac (Rahu
Kalam, Yamagandam, Gulika, Abhijit) splits the daylight period into 8
equal segments whose rotation depends on the weekday.

References:
    - docs/01-thirukanitha-jathakam-calculation.md   §5 (five angas)
    - docs/south-indian-horoscope.md                 §3.6 (almanac segments)
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from enum import StrEnum
from typing import Any
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

import numpy as np
from skyfield import almanac
from skyfield.api import Topos
from skyfield.timelib import Time

from app.core.ephemeris_loader import get_ephemeris
from app.vedic.nakshatra import NAKSHATRA_SPAN_DEG, get_nakshatra_index

# ═══════════════════════════════════════════════════════════════════════ #
# Constants
# ═══════════════════════════════════════════════════════════════════════ #

#: One tithi = 12°; one karana = half a tithi = 6°.
TITHI_SPAN_DEG: np.float64 = np.float64(12.0)
KARANA_SPAN_DEG: np.float64 = np.float64(6.0)

#: One solar day split into the almanac's 8 equal daylight segments.
ALMANAC_SEGMENTS: int = 8


class Paksha(StrEnum):
    """The lunar fortnight — Shukla (Valarpirai, waxing) or Krishna
    (Theipirai, waning)."""

    SHUKLA = "shukla"
    KRISHNA = "krishna"


#: Rahu Kalam segment of the day, indexed by vara (Sunday=0).
#: Transcribed from the concrete windows in docs/south-indian-horoscope.md
#: §3.6: Sunday 4:30–6:00 PM (last), Monday 7:30–9:00 AM (2nd),
#: Tuesday 3:00–4:30 PM (7th), Wednesday 12:00–1:30 PM (5th),
#: Thursday 1:30–3:00 PM (6th), Friday 10:30 AM–12:00 PM (4th),
#: Saturday 9:00–10:30 AM (3rd).
RAHU_KALAM_SEGMENT: tuple[int, ...] = (7, 1, 6, 4, 5, 3, 2)

#: Yamagandam segment of the day, indexed by vara (Sunday=0) — the
#: standard 8-segment rotation paired with Rahu Kalam.
YAMAGANDAM_SEGMENT: tuple[int, ...] = (6, 7, 2, 0, 1, 4, 3)

#: Gulika Kalam segment of the day, indexed by vara (Sunday=0) — the
#: standard 8-segment rotation paired with Rahu Kalam.
GULIKA_SEGMENT: tuple[int, ...] = (3, 4, 5, 6, 7, 0, 1)


@dataclass(frozen=True)
class TimeWindow:
    """A UTC time interval (aware datetimes)."""

    start_utc: datetime
    end_utc: datetime


# ═══════════════════════════════════════════════════════════════════════ #
# The five angas at the birth moment
# ═══════════════════════════════════════════════════════════════════════ #


def get_tithi_index(sun_sidereal_lon: np.float64, moon_sidereal_lon: np.float64) -> int:
    """0-based thithi index (0–29).

    ``Thithi = floor[(Moon_long − Sun_long) / 12°]``, normalised to one
    lunar month; the docs' 1-based "Thithi number" is ``index + 1``.

    References:
        docs/01-thirukanitha-jathakam-calculation.md, §5
    """
    separation = (np.float64(moon_sidereal_lon) - np.float64(sun_sidereal_lon)) % np.float64(360.0)
    return int(separation // TITHI_SPAN_DEG)


def get_tithi_paksha(tithi_index: int) -> Paksha:
    """Paksha of the 0-based tithi index (0–14 Shukla, 15–29 Krishna)."""
    if not 0 <= tithi_index <= 29:
        raise ValueError(f"tithi_index must be in 0..29, got {tithi_index}")
    return Paksha.SHUKLA if tithi_index <= 14 else Paksha.KRISHNA


def get_nakshatra_index_from_moon(moon_sidereal_lon: np.float64) -> int:
    """0-based nakshatra index of the Moon — the Janma Nakshatra.

    ``Nakshatra = floor[Moon_long / 13°20′]``.

    References:
        docs/01-thirukanitha-jathakam-calculation.md, §5
    """
    return get_nakshatra_index(moon_sidereal_lon)


def get_yoga_index(sun_sidereal_lon: np.float64, moon_sidereal_lon: np.float64) -> int:
    """0-based yoga index (0–26).

    ``Yoga = floor[(Sun_long + Moon_long) / 13°20′]``.

    References:
        docs/01-thirukanitha-jathakam-calculation.md, §5
    """
    combined = np.float64(sun_sidereal_lon) + np.float64(moon_sidereal_lon)
    return int(combined % np.float64(360.0) // NAKSHATRA_SPAN_DEG)


def get_karana_sequence_index(sun_sidereal_lon: np.float64, moon_sidereal_lon: np.float64) -> int:
    """0-based karana position in the 60-karana lunar month (0–59).

    Each thithi (12°) splits into 2 karanas of 6° each; the 60 karanas
    of the month are filled by 8 cycles of the 7 chara karanas (0–55)
    followed by the 4 sthira karanas (56–59) at the Amavasya junction.

    References:
        docs/01-thirukanitha-jathakam-calculation.md, §5
    """
    separation = (np.float64(moon_sidereal_lon) - np.float64(sun_sidereal_lon)) % np.float64(360.0)
    return int(separation // KARANA_SPAN_DEG)


def get_karana_id(sequence_index: int) -> int:
    """Karana id in 0..10 from the 60-karana sequence position.

    Ids 0–6 are the chara karanas (Bava … Vishti, cycling 8 times);
    ids 7–10 are the sthira karanas (Shakuni, Chatushpada, Naga,
    Kimstughna) at the month's Amavasya junction.
    """
    if not 0 <= sequence_index <= 59:
        raise ValueError(f"sequence_index must be in 0..59, got {sequence_index}")
    if sequence_index >= 56:
        return 7 + (sequence_index - 56)
    return sequence_index % 7


# ═══════════════════════════════════════════════════════════════════════ #
# Vara — sunrise-anchored weekday
# ═══════════════════════════════════════════════════════════════════════ #


def _weekday_to_vara_index(weekday: int) -> int:
    """Map ``datetime.weekday()`` (Monday=0) to the vara index (Sunday=0)."""
    return (weekday + 1) % 7


def _local_date(value: datetime, timezone: str | None) -> datetime:
    """Convert a UTC datetime to its civil date in ``timezone`` (UTC fallback)."""
    if timezone is None:
        return value
    try:
        return value.astimezone(ZoneInfo(timezone))
    except ZoneInfoNotFoundError:
        raise ValueError(f"unknown IANA timezone: '{timezone}'") from None


def get_vara_index(
    t: Time,
    latitude: float,
    longitude: float,
    timezone: str | None = None,
) -> int:
    """Vara index (Sunday=0) of the Udaya day containing the instant ``t``.

    The Tamil/Hindu civil day runs sunrise to sunrise; the vara of the
    day is the weekday of the civil date on which the most recent
    sunrise occurred. A birth between midnight and sunrise therefore
    carries the weekday of the previous day.

    ``timezone`` is an IANA name used to resolve the sunrise's civil
    date; when ``None`` the UTC date is used. Where the Sun never rises
    or sets (polar conditions) the civil date of ``t`` itself is used.

    References:
        docs/01-thirukanitha-jathakam-calculation.md, §5
    """
    udaya_day = get_udaya_day(t, latitude, longitude)
    if udaya_day is None:
        civil = _local_date(t.utc_datetime(), timezone)
        return _weekday_to_vara_index(civil.weekday())
    anchor, _ = udaya_day
    civil = _local_date(anchor, timezone)
    return _weekday_to_vara_index(civil.weekday())


# ═══════════════════════════════════════════════════════════════════════ #
# Udaya day + daily almanac — Rahu Kalam / Yamagandam / Gulika / Abhijit
# ═══════════════════════════════════════════════════════════════════════ #


def _sunrise_sunset_events(
    t: Time, latitude: float, longitude: float
) -> list[tuple[datetime, bool]]:
    """All sunrise/sunset transitions in ``[t − 1 day, t + 1 day]``.

    Returns ``(utc_datetime, is_sunrise)`` pairs in chronological order.
    """
    eph = get_ephemeris()
    topos = Topos(latitude_degrees=float(latitude), longitude_degrees=float(longitude))
    t0 = t.ts.utc(t.utc_datetime() - timedelta(days=1))
    t1 = t.ts.utc(t.utc_datetime() + timedelta(days=1))
    f = almanac.sunrise_sunset(eph, topos)
    times, events = almanac.find_discrete(t0, t1, f)
    return [
        (event_time.utc_datetime().replace(tzinfo=UTC), bool(event == 1))
        for event_time, event in zip(times, events, strict=True)
    ]


def get_udaya_day(t: Time, latitude: float, longitude: float) -> tuple[datetime, datetime] | None:
    """The Udaya (sunrise-to-sunrise) day containing ``t``.

    Returns ``(sunrise, next_sunrise)`` as aware UTC datetimes, or
    ``None`` when the Sun does not rise or set (polar conditions).

    References:
        docs/south-indian-horoscope.md, §3.6
    """
    events = _sunrise_sunset_events(t, latitude, longitude)
    sunrises = [utc for utc, is_rise in events if is_rise]
    if not sunrises:
        return None
    target = t.utc_datetime()
    prior = [utc for utc in sunrises if utc <= target]
    if not prior:
        return None
    anchor = max(prior)
    following = [utc for utc in sunrises if utc > anchor]
    if not following:
        return None
    return anchor, min(following)


def get_sunset_utc(t: Time, latitude: float, longitude: float) -> datetime | None:
    """Sunset (UTC) of the Udaya day containing ``t``, or ``None``."""
    udaya_day = get_udaya_day(t, latitude, longitude)
    if udaya_day is None:
        return None
    anchor, next_sunrise = udaya_day
    events = _sunrise_sunset_events(t, latitude, longitude)
    for utc, is_rise in events:
        if anchor < utc < next_sunrise and not is_rise:
            return utc
    return None


def get_almanac_segment_windows(
    t: Time, latitude: float, longitude: float
) -> list[TimeWindow] | None:
    """The 8 equal daylight segments of the Udaya day containing ``t``.

    Returns ``None`` when the Sun does not rise or set (polar
    conditions). The segments run from sunrise to sunset.

    References:
        docs/south-indian-horoscope.md, §3.6
    """
    udaya_day = get_udaya_day(t, latitude, longitude)
    if udaya_day is None:
        return None
    anchor, _ = udaya_day
    sunset = get_sunset_utc(t, latitude, longitude)
    if sunset is None:
        return None
    daylight = sunset - anchor
    segment_length = daylight / ALMANAC_SEGMENTS
    return [
        TimeWindow(
            start_utc=anchor + segment_length * index,
            end_utc=anchor + segment_length * (index + 1),
        )
        for index in range(ALMANAC_SEGMENTS)
    ]


def get_rahu_kalam_window(t: Time, latitude: float, longitude: float) -> TimeWindow | None:
    """Rahu Kalam window of the Udaya day containing ``t`` (``None`` polar)."""
    segments = get_almanac_segment_windows(t, latitude, longitude)
    if segments is None:
        return None
    vara_index = get_vara_index(t, latitude, longitude)
    return segments[RAHU_KALAM_SEGMENT[vara_index]]


def get_yamagandam_window(t: Time, latitude: float, longitude: float) -> TimeWindow | None:
    """Yamagandam window of the Udaya day containing ``t`` (``None`` polar)."""
    segments = get_almanac_segment_windows(t, latitude, longitude)
    if segments is None:
        return None
    vara_index = get_vara_index(t, latitude, longitude)
    return segments[YAMAGANDAM_SEGMENT[vara_index]]


def get_gulika_window(t: Time, latitude: float, longitude: float) -> TimeWindow | None:
    """Gulika Kalam window of the Udaya day containing ``t`` (``None`` polar)."""
    segments = get_almanac_segment_windows(t, latitude, longitude)
    if segments is None:
        return None
    vara_index = get_vara_index(t, latitude, longitude)
    return segments[GULIKA_SEGMENT[vara_index]]


def get_abhijit_window(t: Time, latitude: float, longitude: float) -> TimeWindow | None:
    """Abhijit muhurta window: midday ± 1/16 of the daylight duration.

    The period spans one-eighth of the daytime centred on local noon —
    ``start = midday − daylight/16``, ``end = midday + daylight/16``.

    References:
        docs/south-indian-horoscope.md, §3.6
    """
    udaya_day = get_udaya_day(t, latitude, longitude)
    if udaya_day is None:
        return None
    anchor, _ = udaya_day
    sunset = get_sunset_utc(t, latitude, longitude)
    if sunset is None:
        return None
    daylight = sunset - anchor
    midday = anchor + daylight / 2
    half_span = daylight / (2 * ALMANAC_SEGMENTS)
    return TimeWindow(start_utc=midday - half_span, end_utc=midday + half_span)


def get_daily_almanac(
    t: Time,
    latitude: float,
    longitude: float,
    timezone: str | None = None,
) -> dict[str, Any]:
    """Complete daily almanac for the Udaya day containing ``t``.

    Returns a dict with ``vara_index``, the Udaya-day boundaries and the
    four auspicious/inauspicious windows (``None`` windows under polar
    conditions). All datetimes are aware UTC.

    References:
        docs/south-indian-horoscope.md, §3.6
    """
    udaya_day = get_udaya_day(t, latitude, longitude)
    vara_index = get_vara_index(t, latitude, longitude, timezone)
    if udaya_day is None:
        return {"vara_index": vara_index, "available": False}
    anchor, next_sunrise = udaya_day
    return {
        "vara_index": vara_index,
        "available": True,
        "sunrise_utc": anchor,
        "next_sunrise_utc": next_sunrise,
        "sunset_utc": get_sunset_utc(t, latitude, longitude),
        "rahu_kalam": get_rahu_kalam_window(t, latitude, longitude),
        "yamagandam": get_yamagandam_window(t, latitude, longitude),
        "gulika": get_gulika_window(t, latitude, longitude),
        "abhijit": get_abhijit_window(t, latitude, longitude),
    }
