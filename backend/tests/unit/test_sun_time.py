"""Unit tests for local sunrise/sunset computation."""

from __future__ import annotations

from datetime import UTC, datetime

from app.astronomy.sun_time import daylight_hours, get_sunrise_sunset_utc


class TestSunriseSunset:
    def test_chennai_january_2026(self, ts):
        """Chennai (13.08N, 80.27E): Jan 1 sunrise ≈ 06:34 IST = 01:04 UTC."""
        t = ts.utc(2026, 1, 1, 0, 0)
        sunrise, sunset = get_sunrise_sunset_utc(t, 13.0827, 80.2707)
        assert sunrise is not None and sunset is not None
        assert (
            datetime(2026, 1, 1, 0, 30, tzinfo=UTC)
            <= sunrise
            <= datetime(2026, 1, 1, 1, 45, tzinfo=UTC)
        )
        assert (
            datetime(2026, 1, 1, 11, 45, tzinfo=UTC)
            <= sunset
            <= datetime(2026, 1, 1, 13, 15, tzinfo=UTC)
        )

    def test_chennai_june_2026(self, ts):
        """Chennai: mid-June sunrise ≈ 05:45 IST = 00:15 UTC, longer day."""
        t = ts.utc(2026, 6, 15, 0, 0)
        sunrise, sunset = get_sunrise_sunset_utc(t, 13.0827, 80.2707)
        assert sunrise is not None and sunset is not None
        assert (
            datetime(2026, 6, 15, 0, 0, tzinfo=UTC)
            <= sunrise
            <= datetime(2026, 6, 15, 0, 45, tzinfo=UTC)
        )
        assert (
            datetime(2026, 6, 15, 12, 30, tzinfo=UTC)
            <= sunset
            <= datetime(2026, 6, 15, 13, 45, tzinfo=UTC)
        )

    def test_daylight_hours_positive_and_sane(self, ts):
        t = ts.utc(2026, 6, 15, 0, 0)
        hours = daylight_hours(t, 13.0827, 80.2707)
        assert 11.5 < float(hours) < 14.0

    def test_returns_aware_utc_datetimes(self, ts):
        t = ts.utc(2026, 1, 1, 0, 0)
        sunrise, sunset = get_sunrise_sunset_utc(t, 13.0827, 80.2707)
        assert sunrise.tzinfo is not None
        assert sunset.tzinfo is not None
