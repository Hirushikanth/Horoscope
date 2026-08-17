"""Unit tests for the Lahiri (Chitrapaksha) ayanamsa."""

from __future__ import annotations

import numpy as np
import pytest
from app.astronomy.ayanamsa import (
    SPICA,
    AyanamsaSystem,
    get_ayanamsa,
    get_lahiri_ayanamsa,
    tropical_to_sidereal,
)
from app.core.ephemeris_loader import get_earth
from app.exceptions import UnsupportedFeatureError


class TestLahiriAyanamsa:
    def test_spica_anchored_at_180_sidereal(self, ts):
        """Chitrapaksha definition: Chitra (Spica) ≡ 0° Libra = 180° sidereal."""
        t = ts.utc(2026, 8, 10, 0, 0)
        ayanamsa = get_lahiri_ayanamsa(t)
        _, spica_lon, _ = get_earth().at(t).observe(SPICA).ecliptic_latlon(epoch="date")
        sidereal_spica = tropical_to_sidereal(np.float64(spica_lon.degrees), ayanamsa)
        assert abs(float(sidereal_spica) - 180.0) < 1e-9

    def test_value_2026_in_documented_range(self, ts):
        """docs/01 §3: ~24°14′ in 2026; docs/south-indian §3.1: ~24.22°."""
        t = ts.utc(2026, 8, 10, 0, 0)
        ayanamsa = get_lahiri_ayanamsa(t)
        assert 24.0 <= float(ayanamsa) <= 25.0

    def test_precession_rate_about_50_arcsec_per_year(self, ts):
        t_1950 = ts.utc(1950, 1, 1)
        t_2050 = ts.utc(2050, 1, 1)
        delta = float(get_lahiri_ayanamsa(t_2050) - get_lahiri_ayanamsa(t_1950))
        # 100 years × ~50.29″/yr ≈ 1.397°
        assert 1.30 < delta < 1.50

    def test_returns_np_float64(self, ts):
        t = ts.utc(2026, 8, 10)
        assert isinstance(get_lahiri_ayanamsa(t), np.float64)


class TestAyanamsaDispatch:
    def test_default_system_is_lahiri(self, ts):
        t = ts.utc(2026, 8, 10)
        assert float(get_ayanamsa(t)) == float(get_lahiri_ayanamsa(t))

    def test_unimplemented_system_raises(self, ts):
        t = ts.utc(2026, 8, 10)
        with pytest.raises(UnsupportedFeatureError):
            get_ayanamsa(t, AyanamsaSystem.RAMAN)

    def test_tropical_to_sidereal_normalises(self):
        assert float(tropical_to_sidereal(np.float64(10.0), np.float64(20.0))) == 350.0
        assert float(tropical_to_sidereal(np.float64(0.0), np.float64(0.0))) == 0.0
