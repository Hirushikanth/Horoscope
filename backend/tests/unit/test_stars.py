"""Unit tests: yogatara catalogue and proper-motion corrected positions.

Covers the Phase E astronomy module ``app.astronomy.stars``: catalogue
integrity (27 yogataras + navigation stars, unique HIP ids), the
Chitrapaksha anchor invariant (Sidereal(Chitra) ≡ 180°), proper-motion
correction across epochs, float64 discipline and determinism.
"""

from __future__ import annotations

import numpy as np
import pytest
from app.astronomy.ayanamsa import AyanamsaSystem, get_ayanamsa
from app.astronomy.stars import (
    CHITRA_HIP_ID,
    STAR_CATALOG,
    get_star_positions,
    nakshatra_index_of,
)
from app.core.time import build_birth_moment

YOGATARA_ENTRIES = [e for e in STAR_CATALOG if e.associated_nakshatra_index is not None]
EXTRA_ENTRIES = [e for e in STAR_CATALOG if e.associated_nakshatra_index is None]

BIRTH = {"date": "1990-06-15", "time": "06:30:00", "timezone": "Asia/Colombo"}


@pytest.fixture(scope="module")
def birth_ts(ts):
    """Skyfield time of the reference birth instant."""
    moment = build_birth_moment(**BIRTH)
    return moment.skyfield_time


def _positions(birth_ts, ayanamsa):
    return {p.entry.hip_id: p for p in get_star_positions(birth_ts, ayanamsa)}


class TestCatalog:
    def test_has_27_yogataras_and_major_navigation_stars(self):
        assert len(YOGATARA_ENTRIES) == 27
        assert len(EXTRA_ENTRIES) >= 8
        assert len(STAR_CATALOG) == len(YOGATARA_ENTRIES) + len(EXTRA_ENTRIES)

    def test_every_nakshatra_has_exactly_one_yogatara(self):
        associations = [e.associated_nakshatra_index for e in YOGATARA_ENTRIES]
        assert sorted(associations) == list(range(27))

    def test_hip_ids_are_unique(self):
        hip_ids = [e.hip_id for e in STAR_CATALOG]
        assert len(hip_ids) == len(set(hip_ids))

    def test_hip_ids_are_positive_and_names_nonempty(self):
        for entry in STAR_CATALOG:
            assert entry.hip_id > 0
            assert entry.name
            assert entry.designation

    def test_all_catalog_coordinates_are_plausible(self):
        for entry in STAR_CATALOG:
            assert 0.0 <= entry.ra_degrees < 360.0
            assert -90.0 <= entry.dec_degrees <= 90.0
            assert 0.0 <= entry.parallax_mas < 400.0
            assert -2000.0 <= entry.ra_proper_motion <= 2000.0
            assert -2000.0 <= entry.dec_proper_motion <= 2000.0

    def test_chitra_is_in_the_catalog(self):
        chitra = next(e for e in STAR_CATALOG if e.hip_id == CHITRA_HIP_ID)
        assert chitra.name == "Spica"
        assert chitra.associated_nakshatra_index == 13  # Chitra


class TestPositions:
    def test_returns_all_catalog_stars_sorted_brightest_first(self, birth_ts, ts):
        ayanamsa = get_ayanamsa(birth_ts, AyanamsaSystem.LAHIRI)
        positions = get_star_positions(birth_ts, ayanamsa)
        assert len(positions) == len(STAR_CATALOG)
        magnitudes = [p.entry.magnitude for p in positions]
        assert magnitudes == sorted(magnitudes)

    def test_chitra_anchor_sidereal_is_exactly_180(self, birth_ts, ts):
        ayanamsa = get_ayanamsa(birth_ts, AyanamsaSystem.LAHIRI)
        chitra = _positions(birth_ts, ayanamsa)[CHITRA_HIP_ID]
        assert chitra.sidereal_longitude == np.float64(180.0)
        assert chitra.sidereal_longitude == pytest.approx(180.0, abs=1e-9)

    def test_sidereal_is_tropical_minus_ayanamsa(self, birth_ts, ts):
        ayanamsa = get_ayanamsa(birth_ts, AyanamsaSystem.LAHIRI)
        for hip_id, position in _positions(birth_ts, ayanamsa).items():
            if hip_id == CHITRA_HIP_ID:
                continue
            expected = (position.tropical_longitude - ayanamsa) % np.float64(360.0)
            assert position.sidereal_longitude == pytest.approx(expected, abs=1e-9)

    def test_proper_motion_changes_positions_over_time(self, ts):
        """Arcturus (≈2.2″/yr) must move by arcminutes across centuries."""
        moment_1550 = build_birth_moment("1550-06-15", "06:30:00", "Asia/Colombo")
        moment_2000 = build_birth_moment("2000-06-15", "06:30:00", "Asia/Colombo")
        a_1550 = get_ayanamsa(moment_1550.skyfield_time, AyanamsaSystem.LAHIRI)
        a_2000 = get_ayanamsa(moment_2000.skyfield_time, AyanamsaSystem.LAHIRI)
        arcturus_1550 = _positions(moment_1550.skyfield_time, a_1550)[69673]
        arcturus_2000 = _positions(moment_2000.skyfield_time, a_2000)[69673]
        drift_deg = abs(float(arcturus_2000.tropical_longitude - arcturus_1550.tropical_longitude))
        # 450 years × ~2.2 arcsec/yr proper motion → > 0.1° apparent drift
        assert drift_deg > 0.1

    def test_positions_are_float64(self, birth_ts, ts):
        ayanamsa = get_ayanamsa(birth_ts, AyanamsaSystem.LAHIRI)
        for position in get_star_positions(birth_ts, ayanamsa):
            for value in (
                position.ra_hours,
                position.dec_degrees,
                position.tropical_longitude,
                position.sidereal_longitude,
                position.ecliptic_latitude,
                position.distance_light_years,
            ):
                assert isinstance(value, np.float64)

    def test_equatorial_and_ecliptic_ranges_are_valid(self, birth_ts, ts):
        ayanamsa = get_ayanamsa(birth_ts, AyanamsaSystem.LAHIRI)
        for position in get_star_positions(birth_ts, ayanamsa):
            assert 0.0 <= position.ra_hours < 24.0
            assert -90.0 <= position.dec_degrees <= 90.0
            assert 0.0 <= position.tropical_longitude < 360.0
            assert 0.0 <= position.sidereal_longitude < 360.0
            assert -90.0 <= position.ecliptic_latitude <= 90.0
            assert position.distance_light_years > 0.0

    def test_node_convention_is_accepted_for_parity(self, birth_ts, ts):
        ayanamsa = get_ayanamsa(birth_ts, AyanamsaSystem.LAHIRI)
        mean = get_star_positions(birth_ts, ayanamsa, node_convention="mean")
        true = get_star_positions(birth_ts, ayanamsa, node_convention="true")
        assert [p.entry.hip_id for p in mean] == [p.entry.hip_id for p in true]


class TestNakshatraIndex:
    def test_matches_vedic_layer_across_full_sweep(self):
        """The catalog's index convention is identical to the Vedic layer."""
        from app.vedic.nakshatra import get_nakshatra_index

        for degree in range(0, 3600):
            lon = np.float64(degree) / np.float64(10.0)
            assert nakshatra_index_of(lon) == get_nakshatra_index(lon)

    def test_wraps_after_360(self):
        assert nakshatra_index_of(np.float64(359.0)) == 26
        assert nakshatra_index_of(np.float64(0.0)) == 0
        assert nakshatra_index_of(np.float64(361.0)) == 0
