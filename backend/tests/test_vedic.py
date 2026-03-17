"""
Unit tests for the astronomical engine and Vedic calculations.
Cross-validates against known published values.
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
import numpy as np


class TestAyanamsa:
    """Test Lahiri Ayanamsa accuracy against known published values."""

    def test_ayanamsa_j2000(self):
        """At J2000.0 epoch, Lahiri Ayanamsa should be ~23.85° (23°51')."""
        from ephemeris import load_ephemeris, get_ayanamsa
        ts, _ = load_ephemeris()
        t = ts.tt_jd(2451545.0)  # J2000.0
        aya = get_ayanamsa(t)
        # Published value ~23.85° ± 0.05°
        assert abs(aya - 23.85) < 0.1, f"Ayanamsa at J2000.0 = {aya}, expected ~23.85°"

    def test_ayanamsa_2025(self):
        """In 2025, Lahiri Ayanamsa should be ~24.19° (24°11')."""
        from ephemeris import load_ephemeris, get_ayanamsa
        ts, _ = load_ephemeris()
        t = ts.utc(2025, 1, 1, 12, 0, 0)
        aya = get_ayanamsa(t)
        assert abs(aya - 24.19) < 0.15, f"Ayanamsa at 2025 = {aya}, expected ~24.19°"

    def test_ayanamsa_float64(self):
        """Verify ayanamsa returns numpy float64."""
        from ephemeris import load_ephemeris, get_ayanamsa
        ts, _ = load_ephemeris()
        t = ts.tt_jd(2451545.0)
        aya = get_ayanamsa(t)
        assert isinstance(aya, np.floating), f"Ayanamsa type = {type(aya)}, expected np.float64"


class TestNakshatra:
    """Test Nakshatra determination."""

    def test_ashwini_start(self):
        """0° sidereal should be Ashwini."""
        from vedic import get_nakshatra
        nak = get_nakshatra(0.0)
        assert nak['name'] == 'Ashwini'
        assert nak['pada'] == 1

    def test_rohini(self):
        """40° to 53.33° is Rohini."""
        from vedic import get_nakshatra
        nak = get_nakshatra(45.0)
        assert nak['name'] == 'Rohini'

    def test_revati_end(self):
        """359.99° should be Revati."""
        from vedic import get_nakshatra
        nak = get_nakshatra(359.99)
        assert nak['name'] == 'Revati'

    def test_pada_boundaries(self):
        """Test pada calculation within a nakshatra."""
        from vedic import get_nakshatra
        # Each nakshatra = 13.333°, each pada = 3.333°
        nak1 = get_nakshatra(1.0)  # Ashwini pada 1
        assert nak1['pada'] == 1
        nak4 = get_nakshatra(12.0)  # Ashwini pada 4
        assert nak4['pada'] == 4


class TestDasha:
    """Test Vimshottari Dasha calculations."""

    def test_dasha_balance_ashwini_start(self):
        """Moon at exactly 0° = Ashwini start = full Ketu period (7 years)."""
        from vedic import get_janma_nakshatra
        janma = get_janma_nakshatra(0.0)
        assert janma['dasha_lord_at_birth'] == 'Ketu'
        assert abs(janma['dasha_balance_years'] - 7.0) < 0.01

    def test_dasha_sequence(self):
        """Verify the Dasha sequence starts correctly."""
        from vedic import get_vimshottari_dasha
        dasha = get_vimshottari_dasha(0.0, '2000-01-01')
        assert dasha['mahadashas'][0]['lord'] == 'Ketu'
        assert dasha['mahadashas'][1]['lord'] == 'Venus'
        assert dasha['mahadashas'][2]['lord'] == 'Sun'


class TestPanchang:
    """Test Panchang boundary cases."""

    def test_amavasya(self):
        """When Moon-Sun diff ≈ 348-360°, it should be Amavasya."""
        from vedic import get_panchang
        # Sun at 0°, Moon at 355° → diff = 355° → tithi 30 (Amavasya)
        p = get_panchang(0.0, 355.0, 0)
        assert p['tithi']['name'] == 'Amavasya'

    def test_purnima(self):
        """When Moon-Sun diff ≈ 168-180°, it should be Purnima."""
        from vedic import get_panchang
        p = get_panchang(0.0, 175.0, 0)
        assert p['tithi']['name'] == 'Purnima'

    def test_vara_sunday(self):
        """Weekday 0 should be Sunday (Ravivara)."""
        from vedic import get_panchang
        p = get_panchang(0.0, 30.0, 0)
        assert p['vara']['name'] == 'Sunday'
        assert p['vara']['sanskrit'] == 'Ravivara'


class TestRashi:
    """Test Rashi (zodiac sign) determination."""

    def test_mesha(self):
        """0-30° = Mesha (Aries)."""
        from vedic import get_rashi
        r = get_rashi(15.0)
        assert r['name'] == 'Mesha'
        assert r['lord'] == 'Mars'

    def test_meena(self):
        """330-360° = Meena (Pisces)."""
        from vedic import get_rashi
        r = get_rashi(345.0)
        assert r['name'] == 'Meena'
        assert r['lord'] == 'Jupiter'


class TestBhava:
    """Test Bhava (House) assignment."""

    def test_first_house(self):
        """Ascendant sign should be first house."""
        from vedic import get_bhava
        # Asc at 15° (Mesha)
        planets = {'Sun': {'sidereal_longitude': 20.0}}
        bhavas = get_bhava(planets, 15.0)
        assert bhavas[0]['house'] == 1
        assert bhavas[0]['sign'] == 'Mesha'
        assert 'Sun' in bhavas[0]['occupants']


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
