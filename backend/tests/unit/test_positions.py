"""Unit tests for graha position computation."""

from __future__ import annotations

import numpy as np
import pytest
from app.astronomy.ayanamsa import get_ayanamsa, tropical_to_sidereal
from app.astronomy.positions import (
    GRAHA_NAMES,
    get_graha_positions,
    get_mean_lunar_node,
    get_true_lunar_node,
)

SAMPLE_DATES = [
    (2000, 1, 1, 12, 0, 0),
    (1990, 6, 15, 6, 30, 0),
    (2026, 8, 10, 0, 0, 0),
    (1975, 3, 21, 18, 45, 0),
]


class TestGrahaPositions:
    @pytest.mark.parametrize("y,m,d,hh,mm,ss", SAMPLE_DATES)
    def test_nine_grahas_present(self, ts, y, m, d, hh, mm, ss):
        positions = get_graha_positions(ts.utc(y, m, d, hh, mm, ss))
        assert list(positions.keys()) == GRAHA_NAMES

    @pytest.mark.parametrize("y,m,d,hh,mm,ss", SAMPLE_DATES)
    def test_longitudes_in_range(self, ts, y, m, d, hh, mm, ss):
        for pos in get_graha_positions(ts.utc(y, m, d, hh, mm, ss)).values():
            assert 0.0 <= float(pos.tropical_longitude) < 360.0
            assert 0.0 <= float(pos.sidereal_longitude) < 360.0
            assert float(pos.ecliptic_latitude) > -90.0
            assert float(pos.ecliptic_latitude) < 90.0

    @pytest.mark.parametrize("y,m,d,hh,mm,ss", SAMPLE_DATES)
    def test_sidereal_equals_tropical_minus_ayanamsa(self, ts, y, m, d, hh, mm, ss):
        t = ts.utc(y, m, d, hh, mm, ss)
        ayanamsa = get_ayanamsa(t)
        for pos in get_graha_positions(t).values():
            expected = tropical_to_sidereal(pos.tropical_longitude, ayanamsa)
            assert abs(float(pos.sidereal_longitude) - float(expected)) < 1e-9

    @pytest.mark.parametrize("y,m,d,hh,mm,ss", SAMPLE_DATES)
    def test_sun_never_retrograde(self, ts, y, m, d, hh, mm, ss):
        assert get_graha_positions(ts.utc(y, m, d, hh, mm, ss))["Sun"].retrograde is False

    @pytest.mark.parametrize("y,m,d,hh,mm,ss", SAMPLE_DATES)
    def test_moon_never_retrograde(self, ts, y, m, d, hh, mm, ss):
        assert get_graha_positions(ts.utc(y, m, d, hh, mm, ss))["Moon"].retrograde is False

    def test_sun_not_combust(self, ts):
        pos = get_graha_positions(ts.utc(2026, 8, 10))
        assert pos["Sun"].combustion["combust"] is False

    def test_ketu_exactly_opposite_rahu(self, ts):
        positions = get_graha_positions(ts.utc(2026, 8, 10))
        rahu = float(positions["Rahu"].sidereal_longitude)
        ketu = float(positions["Ketu"].sidereal_longitude)
        delta = (ketu - rahu) % 360.0
        assert abs(delta - 180.0) < 1e-9

    def test_all_positions_are_np_float64(self, ts):
        for pos in get_graha_positions(ts.utc(2026, 8, 10)).values():
            assert isinstance(pos.tropical_longitude, np.float64)
            assert isinstance(pos.sidereal_longitude, np.float64)


class TestLunarNodes:
    def test_mean_node_matches_meeus_series(self, ts):
        t = ts.utc(2026, 8, 10)
        centuries = np.float64((t.tt - 2451545.0) / 36525.0)
        expected = (
            np.float64(125.0445479)
            - np.float64(1934.1362891) * centuries
            + np.float64(0.0020754) * centuries * centuries
            + centuries**3 / np.float64(467441.0)
            - centuries**4 / np.float64(60616000.0)
        ) % np.float64(360.0)
        assert abs(float(get_mean_lunar_node(t)) - float(expected)) < 1e-9

    @pytest.mark.parametrize("y,m,d,hh,mm,ss", SAMPLE_DATES)
    def test_true_node_oscillates_within_1_8_deg_of_mean(self, ts, y, m, d, hh, mm, ss):
        """True node deviates ±1.3° from mean; 1.8° bound is generous."""
        t = ts.utc(y, m, d, hh, mm, ss)
        delta = abs(float(get_true_lunar_node(t)) - float(get_mean_lunar_node(t)))
        assert min(delta, 360.0 - delta) < 1.8

    def test_mean_node_always_retrograde(self, ts):
        t = ts.utc(2026, 8, 10)
        positions = get_graha_positions(t)
        assert positions["Rahu"].retrograde is True
        assert positions["Ketu"].retrograde is True

    def test_true_node_convention_used_when_requested(self, ts):
        t = ts.utc(2026, 8, 10)
        mean = get_graha_positions(t, node_convention="mean")["Rahu"]
        true = get_graha_positions(t, node_convention="true")["Rahu"]
        delta = abs(float(mean.sidereal_longitude) - float(true.sidereal_longitude))
        assert 0.01 < min(delta, 360.0 - delta) < 1.8
