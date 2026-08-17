"""Unit tests for the Lagna (ascendant) computation.

The ascendant formula is verified independently: the returned ecliptic
longitude must place a point whose altitude on the celestial sphere is
exactly zero (on the horizon), with the body rising (hour angle < 0).
"""

from __future__ import annotations

import numpy as np
from app.astronomy.ascendant import (
    get_ascendant,
    get_gmst_degrees,
    get_obliquity,
    get_sidereal_ascendant,
)
from app.astronomy.ayanamsa import get_ayanamsa

CASES = [
    (2000, 1, 1, 12, 0, 0, 13.0827, 80.2707),  # Chennai
    (1990, 6, 15, 6, 30, 0, 6.9271, 79.8612),  # Colombo
    (2026, 8, 10, 0, 0, 0, 51.5074, -0.1278),  # London
    (1975, 3, 21, 18, 45, 0, 40.7128, -74.0060),  # New York
    (2026, 12, 31, 23, 59, 59, -33.8688, 151.2093),  # Sydney
]


def _horizon_altitude_radians(t, latitude, longitude, lambda_deg) -> float:
    """Altitude (radians) of the ecliptic point at ``lambda_deg``."""
    lst = np.radians(np.float64(get_gmst_degrees(t)) + np.float64(longitude))
    eps = np.radians(get_obliquity(t))
    lam = np.radians(np.float64(lambda_deg))
    phi = np.radians(np.float64(latitude))

    dec = np.arcsin(np.sin(eps) * np.sin(lam))
    ra = np.arctan2(np.cos(eps) * np.sin(lam), np.cos(lam))
    hour_angle = lst - ra

    altitude = np.arcsin(np.sin(phi) * np.sin(dec) + np.cos(phi) * np.cos(dec) * np.cos(hour_angle))
    return float(altitude)


def _rising(t, latitude, longitude, lambda_deg) -> bool:
    """True when the ecliptic point at ``lambda_deg`` is rising (east)."""
    lst = np.radians(np.float64(get_gmst_degrees(t)) + np.float64(longitude))
    eps = np.radians(get_obliquity(t))
    lam = np.radians(np.float64(lambda_deg))
    ra = np.arctan2(np.cos(eps) * np.sin(lam), np.cos(lam))
    return float(np.sin(lst - ra)) < 0.0


class TestGMST:
    def test_gmst_range(self, ts):
        for y, m, d, hh, mm, ss, _, _ in CASES:
            gmst = get_gmst_degrees(ts.utc(y, m, d, hh, mm, ss))
            assert 0.0 <= float(gmst) < 360.0

    def test_obliquity_2026_about_23_44(self, ts):
        eps = get_obliquity(ts.utc(2026, 8, 10))
        assert 23.40 < float(eps) < 23.46


class TestAscendant:
    def test_equator_zero_lst_gives_90_deg(self, ts):
        """At the equator with LST = 0, the rising point is λ = 90°."""
        t = ts.utc(2000, 3, 20, 12, 0, 0)  # vernal equinox epoch
        longitude = float(-get_gmst_degrees(t)) % 360.0  # force LST = 0
        asc = get_ascendant(t, 0.0, longitude)
        assert abs(float(asc) - 90.0) < 1e-6

    def test_ascendant_on_horizon(self, ts):
        """Independent verification: altitude of the ascendant is ~0."""
        for y, m, d, hh, mm, ss, lat, lon in CASES:
            t = ts.utc(y, m, d, hh, mm, ss)
            asc = float(get_ascendant(t, lat, lon))
            assert abs(_horizon_altitude_radians(t, lat, lon, asc)) < 1e-9

    def test_ascendant_is_rising_not_setting(self, ts):
        for y, m, d, hh, mm, ss, lat, lon in CASES:
            t = ts.utc(y, m, d, hh, mm, ss)
            asc = float(get_ascendant(t, lat, lon))
            assert _rising(t, lat, lon, asc) is True
            # the descendant (180° away) must be setting
            assert _rising(t, lat, lon, (asc + 180.0) % 360.0) is False

    def test_antipode_also_on_horizon(self, ts):
        for y, m, d, hh, mm, ss, lat, lon in CASES:
            t = ts.utc(y, m, d, hh, mm, ss)
            asc = float(get_ascendant(t, lat, lon))
            desc = (asc + 180.0) % 360.0
            assert abs(_horizon_altitude_radians(t, lat, lon, desc)) < 1e-9

    def test_sidereal_ascendant_uses_ayanamsa(self, ts):
        for y, m, d, hh, mm, ss, lat, lon in CASES:
            t = ts.utc(y, m, d, hh, mm, ss)
            ayanamsa = get_ayanamsa(t)
            sid = float(get_sidereal_ascendant(t, lat, lon, ayanamsa))
            tropical = float(get_ascendant(t, lat, lon))
            expected = (tropical - float(ayanamsa)) % 360.0
            assert abs(sid - expected) < 1e-9

    def test_lagna_moves_about_1_deg_per_4_minutes(self, ts):
        """docs/01 §6: the lagna shifts ≈1° every 4 minutes."""
        t = ts.utc(2026, 8, 10, 6, 0, 0)
        t_plus = ts.utc(2026, 8, 10, 6, 4, 0)
        delta = float(get_ascendant(t_plus, 13.0827, 80.2707) - get_ascendant(t, 13.0827, 80.2707))
        delta = abs(delta % 360.0)
        assert 0.5 < min(delta, 360.0 - delta) < 1.5
