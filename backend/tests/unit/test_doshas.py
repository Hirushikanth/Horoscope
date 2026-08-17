"""Unit tests for Chevvai Dosham (docs/01 §12).

The dosha houses are {1, 2, 4, 7, 8, 12} counted from each of the three
reference points (Lagna, Moon, Venus); the report records the presence
and from how many references the dosha arises.
"""

from __future__ import annotations

import numpy as np
from app.vedic.doshas import _dosha_houses_from, assess_chevvai_dosham


def _lon(rasi_index: int, degree: float = 15.0) -> np.float64:
    return np.float64(rasi_index * 30.0 + degree)


def test_no_dosha_when_mars_outside_dosha_houses():
    # Lagna Mesha, Mars in Mithuna (house 3) — all three references clear
    report = assess_chevvai_dosham(
        mars_sidereal_lon=_lon(2),
        lagna_sidereal_lon=_lon(0),
        moon_sidereal_lon=_lon(0),
        venus_sidereal_lon=_lon(0),
    )
    assert not report.present
    assert report.reference_count == 0
    assert report.houses_from_lagna == ()
    assert report.houses_from_moon == ()
    assert report.houses_from_venus == ()


def test_dosha_from_lagna_only():
    # Mars in Vrischika (rasi 7) is house 8 from Mesha lagna → dosha.
    # From Moon in Kanya (rasi 5): Mars is house 3 → no dosha.
    # From Venus in Karka (rasi 3): Mars is house 5 → no dosha.
    report = assess_chevvai_dosham(
        mars_sidereal_lon=_lon(7),
        lagna_sidereal_lon=_lon(0),
        moon_sidereal_lon=_lon(5),
        venus_sidereal_lon=_lon(3),
    )
    assert report.present
    assert report.reference_count == 1
    assert report.houses_from_lagna == (8,)
    assert report.houses_from_moon == ()
    assert report.houses_from_venus == ()


def test_dosha_from_multiple_references():
    # Lagna Mesha, Mars in Karka (rasi 3) → house 4 from lagna, house 4 from
    # Moon in Mesha, house 2 from Venus in Mithuna
    report = assess_chevvai_dosham(
        mars_sidereal_lon=_lon(3),
        lagna_sidereal_lon=_lon(0),
        moon_sidereal_lon=_lon(0),
        venus_sidereal_lon=_lon(2),
    )
    assert report.present
    assert report.reference_count == 3
    assert report.houses_from_lagna == (4,)
    assert report.houses_from_moon == (4,)
    assert report.houses_from_venus == (2,)


def test_dosha_houses_are_exactly_the_classical_set():
    """Mars in each of houses 1,2,4,7,8,12 from the lagna → dosha;
    houses 3,5,6,9,10,11 → no dosha."""
    dosha_houses = {1, 2, 4, 7, 8, 12}
    for house in range(1, 13):
        mars_rasi = (house - 1) % 12
        result = _dosha_houses_from(mars_rasi, 0)
        assert result == ((house,) if house in dosha_houses else ()), house


def test_dosha_counted_from_moon_and_venus_signs():
    # Mars in Karka (rasi 3): from Moon in Karka → house 1 (dosha)
    report = assess_chevvai_dosham(
        mars_sidereal_lon=_lon(3),
        lagna_sidereal_lon=_lon(5),
        moon_sidereal_lon=_lon(3),
        venus_sidereal_lon=_lon(5),
    )
    assert report.houses_from_moon == (1,)
    assert report.houses_from_lagna == ()
    assert report.houses_from_venus == ()
