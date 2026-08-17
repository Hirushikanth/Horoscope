"""Unit tests for the five angas and the daily almanac.

The angular formulas (thithi, yogam, karanam, nakshatram) are pure
math cross-checked against the docs' worked values; the vara and the
almanac windows are verified against the sunrise-anchored Udaya day
for Chennai (docs/01 §5, docs/south-indian-horoscope.md §3.6).
"""

from __future__ import annotations

from datetime import UTC, timedelta

import numpy as np
import pytest
from app.vedic.nakshatra import NAKSHATRA_SPAN_DEG
from app.vedic.panchangam import (
    ALMANAC_SEGMENTS,
    GULIKA_SEGMENT,
    KARANA_SPAN_DEG,
    RAHU_KALAM_SEGMENT,
    TITHI_SPAN_DEG,
    YAMAGANDAM_SEGMENT,
    Paksha,
    get_abhijit_window,
    get_almanac_segment_windows,
    get_daily_almanac,
    get_karana_id,
    get_karana_sequence_index,
    get_nakshatra_index_from_moon,
    get_rahu_kalam_window,
    get_tithi_index,
    get_tithi_paksha,
    get_udaya_day,
    get_vara_index,
    get_yamagandam_window,
    get_yoga_index,
)

CHENNAI_LAT = 13.0827
CHENNAI_LON = 80.2707


# ═══════════════════════════════════════════════════════════════════════ #
# Thithi
# ═══════════════════════════════════════════════════════════════════════ #


def test_tithi_index_matches_docs_worked_values():
    # Moon ahead of Sun by 0°, 12°, 24° → tithis 1, 2, 3 (indices 0, 1, 2)
    assert get_tithi_index(np.float64(0.0), np.float64(0.0)) == 0
    assert get_tithi_index(np.float64(0.0), np.float64(TITHI_SPAN_DEG)) == 1
    assert get_tithi_index(np.float64(0.0), np.float64(2 * TITHI_SPAN_DEG)) == 2
    # separation 180° → Purnima (index 15); 181° → Krishna Pratipada (index 15)
    assert get_tithi_index(np.float64(0.0), np.float64(180.0)) == 15
    assert get_tithi_index(np.float64(0.0), np.float64(181.0)) == 15
    # just below a boundary stays in the previous tithi
    assert get_tithi_index(np.float64(0.0), np.float64(2 * TITHI_SPAN_DEG - 0.001)) == 1
    # separation wraps: Moon slightly behind Sun → last tithi (Amavasya)
    assert get_tithi_index(np.float64(5.0), np.float64(0.0)) == 29


def test_tithi_span_is_12_degrees():
    assert float(TITHI_SPAN_DEG) == 12.0
    assert float(TITHI_SPAN_DEG) * 30.0 == 360.0


def test_tithi_paksha_boundaries():
    for index in range(15):
        assert get_tithi_paksha(index) is Paksha.SHUKLA
    for index in range(15, 30):
        assert get_tithi_paksha(index) is Paksha.KRISHNA
    with pytest.raises(ValueError):
        get_tithi_paksha(30)
    with pytest.raises(ValueError):
        get_tithi_paksha(-1)


# ═══════════════════════════════════════════════════════════════════════ #
# Nakshatram (from the Moon)
# ═══════════════════════════════════════════════════════════════════════ #


def test_nakshatra_index_from_moon():
    assert get_nakshatra_index_from_moon(np.float64(0.0)) == 0
    assert get_nakshatra_index_from_moon(np.float64(NAKSHATRA_SPAN_DEG)) == 1
    assert get_nakshatra_index_from_moon(np.float64(26 * NAKSHATRA_SPAN_DEG)) == 26
    assert get_nakshatra_index_from_moon(np.float64(359.0)) == 26


# ═══════════════════════════════════════════════════════════════════════ #
# Yogam
# ═══════════════════════════════════════════════════════════════════════ #


def test_yoga_index_matches_docs_worked_values():
    # Sun 10°, Moon 20° → combined 30° → 30 / 13°20′ = 2 (Preeti)
    assert get_yoga_index(np.float64(10.0), np.float64(20.0)) == 2
    # combined exactly at a boundary starts the next yoga
    assert get_yoga_index(np.float64(0.0), np.float64(NAKSHATRA_SPAN_DEG)) == 1
    # wrap-around: combined 720° − 2° → 358° → index 26 (Vaidhriti)
    assert get_yoga_index(np.float64(359.0), np.float64(359.0)) == 26
    # combined 30° exactly → index 2
    assert get_yoga_index(np.float64(30.0), np.float64(0.0)) == 2


# ═══════════════════════════════════════════════════════════════════════ #
# Karanam
# ═══════════════════════════════════════════════════════════════════════ #


def test_karana_sequence_index():
    assert get_karana_sequence_index(np.float64(0.0), np.float64(0.0)) == 0
    assert get_karana_sequence_index(np.float64(0.0), np.float64(KARANA_SPAN_DEG)) == 1
    assert get_karana_sequence_index(np.float64(0.0), np.float64(6 * KARANA_SPAN_DEG)) == 6
    # the 60th karana wraps around the lunar month
    assert get_karana_sequence_index(np.float64(0.0), np.float64(60 * KARANA_SPAN_DEG)) == 0
    assert get_karana_sequence_index(np.float64(0.0), np.float64(355.0)) == 59
    assert get_karana_sequence_index(np.float64(5.0), np.float64(0.0)) == 59


def test_karana_id_rotation():
    """Chara karanas cycle 8 times (indices 0–55), then the 4 sthira."""
    assert get_karana_id(0) == 0  # Bava
    assert get_karana_id(6) == 6  # Vishti
    assert get_karana_id(7) == 0  # cycle restarts — Bava again
    assert get_karana_id(55) == 6  # 8th Vishti
    assert get_karana_id(56) == 7  # Shakuni
    assert get_karana_id(57) == 8  # Chatushpada
    assert get_karana_id(58) == 9  # Naga
    assert get_karana_id(59) == 10  # Kimstughna
    with pytest.raises(ValueError):
        get_karana_id(60)
    with pytest.raises(ValueError):
        get_karana_id(-1)


# ═══════════════════════════════════════════════════════════════════════ #
# Vara — sunrise-anchored weekday (Chennai)
# ═══════════════════════════════════════════════════════════════════════ #


@pytest.fixture(scope="module")
def chennai_time(ts):
    return lambda year, month, day, hour, minute: ts.utc(year, month, day, hour, minute)


def test_vara_at_noon_is_the_civil_weekday(chennai_time):
    # 2024-03-15 06:30 UTC = 12:00 IST, well after sunrise → Friday (vara 5)
    t = chennai_time(2024, 3, 15, 6, 30)
    assert get_vara_index(t, CHENNAI_LAT, CHENNAI_LON) == 5


def test_vara_before_sunrise_is_previous_civil_day(chennai_time):
    # 2024-03-15 00:00 UTC = 05:30 IST — before Chennai's sunrise (~06:10 IST),
    # so the Udaya day still belongs to Thursday (vara 4)
    t = chennai_time(2024, 3, 15, 0, 0)
    assert get_vara_index(t, CHENNAI_LAT, CHENNAI_LON) == 4


def test_vara_with_timezone(chennai_time):
    t = chennai_time(2024, 3, 15, 6, 30)
    assert get_vara_index(t, CHENNAI_LAT, CHENNAI_LON, "Asia/Kolkata") == 5
    assert get_vara_index(t, CHENNAI_LAT, CHENNAI_LON, "UTC") == 5


def test_udaya_day_contains_the_instant(chennai_time):
    t = chennai_time(2024, 3, 15, 6, 30)
    udaya_day = get_udaya_day(t, CHENNAI_LAT, CHENNAI_LON)
    assert udaya_day is not None
    sunrise, next_sunrise = udaya_day
    assert sunrise.tzinfo is UTC
    assert sunrise < t.utc_datetime() < next_sunrise
    assert next_sunrise - sunrise < timedelta(hours=25)


def test_polar_day_has_no_udaya_day(ts):
    # Svalbard in polar night — the Sun never rises
    t = ts.utc(2024, 1, 1, 12, 0)
    assert get_udaya_day(t, 78.2232, 15.6469) is None
    # vara falls back to the civil weekday: 2024-01-01 was a Monday → vara 1
    assert get_vara_index(t, 78.2232, 15.6469) == 1


# ═══════════════════════════════════════════════════════════════════════ #
# Daily almanac — segment windows
# ═══════════════════════════════════════════════════════════════════════ #


def test_almanac_segments_tile_the_daylight(chennai_time):
    t = chennai_time(2024, 3, 15, 6, 30)
    segments = get_almanac_segment_windows(t, CHENNAI_LAT, CHENNAI_LON)
    assert segments is not None
    assert len(segments) == ALMANAC_SEGMENTS
    sunrise, next_sunrise = get_udaya_day(t, CHENNAI_LAT, CHENNAI_LON)
    assert sunrise is not None
    for previous, current in zip(segments[:-1], segments[1:], strict=True):
        assert previous.end_utc == current.start_utc
        assert current.end_utc - current.start_utc == previous.end_utc - previous.start_utc


def test_rahu_kalam_segment_rotation(chennai_time):
    """Rahu Kalam is always the segment prescribed for the day's vara."""
    for civil_date, expected_vara in ((15, 5), (16, 6), (17, 0)):  # Fri, Sat, Sun
        t = chennai_time(2024, 3, civil_date, 6, 30)
        vara = get_vara_index(t, CHENNAI_LAT, CHENNAI_LON)
        assert vara == expected_vara
        segments = get_almanac_segment_windows(t, CHENNAI_LAT, CHENNAI_LON)
        assert segments is not None
        rahu = get_rahu_kalam_window(t, CHENNAI_LAT, CHENNAI_LON)
        assert rahu == segments[RAHU_KALAM_SEGMENT[vara]]
        yamagandam = get_yamagandam_window(t, CHENNAI_LAT, CHENNAI_LON)
        assert yamagandam == segments[YAMAGANDAM_SEGMENT[vara]]
        gulika = get_daily_almanac(t, CHENNAI_LAT, CHENNAI_LON)["gulika"]
        assert gulika == segments[GULIKA_SEGMENT[vara]]


def test_sunday_rahu_kalam_matches_docs_slot(chennai_time):
    """docs §3.6: Sunday's Rahu Kalam is the last segment (4:30–6:00 PM)."""
    t = chennai_time(2024, 3, 17, 6, 30)  # Sunday
    assert get_vara_index(t, CHENNAI_LAT, CHENNAI_LON) == 0
    segments = get_almanac_segment_windows(t, CHENNAI_LAT, CHENNAI_LON)
    assert segments is not None
    assert get_rahu_kalam_window(t, CHENNAI_LAT, CHENNAI_LON) == segments[7]


def test_abhijit_is_midday_centered(chennai_time):
    t = chennai_time(2024, 3, 15, 6, 30)
    abhijit = get_abhijit_window(t, CHENNAI_LAT, CHENNAI_LON)
    assert abhijit is not None
    sunrise, _ = get_udaya_day(t, CHENNAI_LAT, CHENNAI_LON)
    assert sunrise is not None
    sunset = get_daily_almanac(t, CHENNAI_LAT, CHENNAI_LON)["sunset_utc"]
    assert sunset is not None
    midpoint = abhijit.start_utc + (abhijit.end_utc - abhijit.start_utc) / 2
    expected_midday = sunrise + (sunset - sunrise) / 2
    assert abs((midpoint - expected_midday).total_seconds()) < 60


def test_daily_almanac_shape(chennai_time):
    t = chennai_time(2024, 3, 15, 6, 30)
    almanac = get_daily_almanac(t, CHENNAI_LAT, CHENNAI_LON)
    assert almanac["available"] is True
    assert almanac["vara_index"] == 5
    assert set(almanac) == {
        "vara_index",
        "available",
        "sunrise_utc",
        "next_sunrise_utc",
        "sunset_utc",
        "rahu_kalam",
        "yamagandam",
        "gulika",
        "abhijit",
    }
    for key in ("rahu_kalam", "yamagandam", "gulika", "abhijit"):
        assert almanac[key] is not None
        assert almanac[key].start_utc < almanac[key].end_utc


def test_daily_almanac_polar(ts):
    t = ts.utc(2024, 1, 1, 12, 0)
    almanac = get_daily_almanac(t, 78.2232, 15.6469)
    assert almanac == {"vara_index": 1, "available": False}
