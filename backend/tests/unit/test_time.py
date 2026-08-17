"""Unit tests for core time handling."""

from __future__ import annotations

import numpy as np
import pytest
from app.core.time import build_birth_moment, validate_jd_in_range
from app.exceptions import InvalidBirthDataError


class TestBuildBirthMoment:
    def test_jd_at_j2000_epoch(self):
        # 2000-01-01 17:30 IST == 2000-01-01 12:00 UTC == JD 2451545.0
        moment = build_birth_moment("2000-01-01", "17:30:00", "Asia/Kolkata")
        assert abs(float(moment.jd_ut1) - 2451545.0) < 1.2e-5  # UT1-UTC < 0.9s

    def test_utc_conversion_is_aware_and_correct(self):
        moment = build_birth_moment("2026-08-10", "06:30:00", "Asia/Kolkata")
        assert moment.utc.tzinfo is not None
        assert moment.utc.hour == 1  # IST = UTC+5:30
        assert moment.utc.day == 10

    def test_dst_winter_offset_new_york(self):
        moment = build_birth_moment("2025-01-01", "10:00:00", "America/New_York")
        assert moment.utc.hour == 15  # EST = UTC-5

    def test_dst_summer_offset_new_york(self):
        moment = build_birth_moment("2025-07-01", "10:00:00", "America/New_York")
        assert moment.utc.hour == 14  # EDT = UTC-4

    def test_seconds_default_to_zero(self):
        moment = build_birth_moment("2026-08-10", "06:30", "Asia/Kolkata")
        assert moment.local.second == 0

    def test_microsecond_precision_preserved(self):
        moment = build_birth_moment("2026-08-10", "06:30:15.5", "Asia/Kolkata")
        assert moment.local.microsecond == 500_000

    def test_invalid_timezone_raises(self):
        with pytest.raises(InvalidBirthDataError):
            build_birth_moment("2026-08-10", "06:30", "Not/AZone")

    def test_malformed_date_raises(self):
        with pytest.raises(InvalidBirthDataError):
            build_birth_moment("10-08-2026", "06:30", "Asia/Kolkata")

    def test_out_of_range_components_raise(self):
        with pytest.raises(InvalidBirthDataError):
            build_birth_moment("2026-13-40", "06:30", "Asia/Kolkata")


class TestValidateJdInRange:
    def test_modern_date_ok(self):
        moment = build_birth_moment("2026-08-10", "06:30", "Asia/Kolkata")
        validate_jd_in_range(moment.jd_ut1)  # must not raise

    def test_ancient_date_rejected(self):
        moment = build_birth_moment("1500-01-01", "00:00", "Asia/Kolkata")
        with pytest.raises(Exception) as excinfo:
            validate_jd_in_range(moment.jd_ut1)
        assert "DE440" in str(excinfo.value)

    def test_future_date_rejected(self):
        from app.exceptions import DateOutOfRangeError

        moment = build_birth_moment("3000-01-01", "00:00", "Asia/Kolkata")
        with pytest.raises(DateOutOfRangeError):
            validate_jd_in_range(moment.jd_ut1)


class TestFloat64Guarantees:
    def test_jd_is_np_float64(self):
        moment = build_birth_moment("2026-08-10", "06:30", "Asia/Kolkata")
        assert isinstance(moment.jd_ut1, np.float64)
