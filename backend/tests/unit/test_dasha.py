"""Unit tests for Vimshottari Dasa (docs/01 §11).

The tests verify the balance formula against every nakshatra boundary,
the antardasha/pratyantardasha proportionality, timeline contiguity and
the 360 vs 365.25 year-length switch.
"""

from __future__ import annotations

import numpy as np
import pytest
from app.vedic.dasha import (
    DEFAULT_YEAR_LENGTH_DAYS,
    TAMIL_YEAR_LENGTH_DAYS,
    VIMSHOTTARI_SEQUENCE,
    VIMSHOTTARI_TOTAL_YEARS,
    VIMSHOTTARI_YEARS,
    balance_years_to_days,
    vimshottari_balance,
    vimshottari_timeline,
)
from app.vedic.nakshatra import NAKSHATRA_SPAN_DEG, get_nakshatra_index
from app.vedic.tables import Graha

START_JD = np.float64(2460000.5)


# ═══════════════════════════════════════════════════════════════════════ #
# Balance
# ═══════════════════════════════════════════════════════════════════════ #


def test_balance_at_nakshatra_start_is_full():
    """Moon just inside a nakshatra start → full lord years remain."""
    for nakshatra_index in range(27):
        moon_lon = np.float64(nakshatra_index) * NAKSHATRA_SPAN_DEG + 1e-6
        balance = vimshottari_balance(moon_lon)
        expected_lord = VIMSHOTTARI_SEQUENCE[nakshatra_index % 9]
        assert balance.lord is expected_lord, nakshatra_index
        assert np.isclose(balance.fraction_remaining, 1.0)
        assert np.isclose(balance.balance_years, float(VIMSHOTTARI_YEARS[expected_lord]))


def test_balance_halfway_through_nakshatra():
    # Ashwini midpoint (6°40′) — Ketu's half of 7 years remains
    moon_lon = NAKSHATRA_SPAN_DEG / 2
    balance = vimshottari_balance(moon_lon)
    assert balance.lord is Graha.KETU
    assert np.isclose(balance.fraction_remaining, 0.5)
    assert np.isclose(balance.balance_years, 3.5)


def test_balance_at_nakshatra_end_is_zero():
    """Moon just before the next nakshatra → balance ≈ 0."""
    moon_lon = NAKSHATRA_SPAN_DEG - 1e-6
    balance = vimshottari_balance(moon_lon)
    assert balance.lord is Graha.KETU
    assert balance.fraction_remaining < 1e-5
    assert balance.balance_years < 1e-4


# ═══════════════════════════════════════════════════════════════════════ #
# Timeline — mahadasha level (depth 1)
# ═══════════════════════════════════════════════════════════════════════ #


def test_timeline_full_cycle_when_balance_is_full():
    """Moon at nakshatra 0 → balance 7y Ketu; 9 mahadashas span exactly 120y."""
    timeline = vimshottari_timeline(START_JD, np.float64(0.0), depth=1)
    mahadashas = timeline
    assert len(mahadashas) == 9
    assert mahadashas[0].graha is Graha.KETU
    assert np.isclose(float(mahadashas[0].years), 7.0)
    expected_cycle = list(VIMSHOTTARI_SEQUENCE)
    for period, expected_lord in zip(mahadashas, expected_cycle, strict=True):
        assert period.graha is expected_lord
        assert period.category == "mahadasha"
        assert period.parent_index is None
    total_years = sum(float(p.years) for p in mahadashas)
    assert np.isclose(total_years, 120.0)
    total_days = sum(float(p.days) for p in mahadashas)
    assert np.isclose(total_days, 120.0 * float(DEFAULT_YEAR_LENGTH_DAYS))
    # first period starts at the birth instant; periods are contiguous
    assert np.isclose(float(mahadashas[0].start_jd), float(START_JD))
    for previous, current in zip(mahadashas[:-1], mahadashas[1:], strict=True):
        assert np.isclose(float(previous.end_jd), float(current.start_jd))


def test_timeline_balance_first_period():
    """Halfway balance shortens the first mahadasha and lengthens the span."""
    moon_lon = NAKSHATRA_SPAN_DEG / 2  # Ashwini midpoint, Ketu balance 3.5y
    timeline = vimshottari_timeline(START_JD, moon_lon, depth=1)
    assert timeline[0].graha is Graha.KETU
    assert np.isclose(float(timeline[0].years), 3.5)
    # cycle continues Venus after the balance period
    assert timeline[1].graha is Graha.SUKRA
    assert np.isclose(float(timeline[1].years), 20.0)
    total_years = sum(float(p.years) for p in timeline)
    assert total_years >= 120.0
    assert np.isclose(float(timeline[0].start_jd), float(START_JD))


def test_timeline_requires_valid_depth():
    with pytest.raises(ValueError):
        vimshottari_timeline(START_JD, np.float64(0.0), depth=4)
    with pytest.raises(ValueError):
        vimshottari_timeline(START_JD, np.float64(0.0), depth=0)


# ═══════════════════════════════════════════════════════════════════════ #
# Antardasha (depth 2) and pratyantardasha (depth 3)
# ═══════════════════════════════════════════════════════════════════════ #


def test_antardashas_sum_to_mahadasha():
    timeline = vimshottari_timeline(START_JD, np.float64(0.0), depth=2)
    mahadashas = [p for p in timeline if p.category == "mahadasha"]
    antardashas = [p for p in timeline if p.category == "antardasha"]
    assert len(mahadashas) == 9
    assert len(antardashas) == 9 * 9
    for md in mahadashas:
        children = [p for p in antardashas if p.parent_index == timeline.index(md)]
        assert len(children) == 9
        assert np.isclose(sum(float(p.years) for p in children), float(md.years), atol=1e-9)
        # the child antardashas tile the parent period without gaps
        assert np.isclose(float(children[0].start_jd), float(md.start_jd))
        for previous, current in zip(children[:-1], children[1:], strict=True):
            assert np.isclose(float(previous.end_jd), float(current.start_jd))
        assert np.isclose(float(children[-1].end_jd), float(md.end_jd))


def test_pratyantardashas_sum_to_antardasha():
    timeline = vimshottari_timeline(START_JD, np.float64(0.0), depth=3)
    antardashas = [p for p in timeline if p.category == "antardasha"]
    pratyantardashas = [p for p in timeline if p.category == "pratyantardasha"]
    assert len(pratyantardashas) == 9 * 9 * 9
    for ad in antardashas:
        children = [p for p in pratyantardashas if p.parent_index == timeline.index(ad)]
        assert len(children) == 9
        assert np.isclose(sum(float(p.years) for p in children), float(ad.years), atol=1e-9)


def test_first_pratyantardasha_matches_classical_example():
    """Ketu mahadasha 7y: Ketu antardasha = 7×7/120 = 0.408333y;
    first pratyantardasha (Ketu within Ketu) = 0.408333×7/120."""
    timeline = vimshottari_timeline(START_JD, np.float64(0.0), depth=3)
    mahadasha = timeline[0]
    assert mahadasha.graha is Graha.KETU
    assert np.isclose(float(mahadasha.years), 7.0)
    first_ad = timeline[1]
    assert first_ad.category == "antardasha"
    assert first_ad.graha is Graha.KETU
    assert np.isclose(float(first_ad.years), 7.0 * 7.0 / 120.0)
    first_pd = timeline[2]
    assert first_pd.category == "pratyantardasha"
    assert first_pd.graha is Graha.KETU
    assert np.isclose(float(first_pd.years), 7.0 * 7.0 / 120.0 * 7.0 / 120.0)


def test_sequence_rotation_through_lords():
    """After Ketu the antardasha lords rotate in the fixed order."""
    timeline = vimshottari_timeline(START_JD, np.float64(0.0), depth=2)
    ketu_md = timeline[0]
    children = [p for p in timeline[1:10]]
    for child, expected in zip(children, list(VIMSHOTTARI_SEQUENCE), strict=True):
        assert child.graha is expected
        assert child.parent_index == timeline.index(ketu_md)


# ═══════════════════════════════════════════════════════════════════════ #
# Year length switch (360 Tamil days)
# ═══════════════════════════════════════════════════════════════════════ #


def test_year_length_switch_changes_days_not_years():
    for year_length in (365.25, 360.0):
        timeline = vimshottari_timeline(
            START_JD, np.float64(0.0), depth=1, year_length_days=year_length
        )
        assert np.isclose(sum(float(p.years) for p in timeline), 120.0)
        assert np.isclose(sum(float(p.days) for p in timeline), 120.0 * year_length)


def test_balance_years_to_days():
    assert np.isclose(
        float(balance_years_to_days(np.float64(3.5), float(DEFAULT_YEAR_LENGTH_DAYS))),
        3.5 * float(DEFAULT_YEAR_LENGTH_DAYS),
    )
    assert np.isclose(
        float(balance_years_to_days(np.float64(3.5), float(TAMIL_YEAR_LENGTH_DAYS))),
        3.5 * float(TAMIL_YEAR_LENGTH_DAYS),
    )


# ═══════════════════════════════════════════════════════════════════════ #
# Cross-consistency with the nakshatra module
# ═══════════════════════════════════════════════════════════════════════ #


def test_balance_lord_matches_nakshatra_lord():
    for nakshatra_index in range(27):
        moon_lon = np.float64(nakshatra_index) * NAKSHATRA_SPAN_DEG + 5.0
        assert (
            vimshottari_balance(moon_lon).lord
            is VIMSHOTTARI_SEQUENCE[get_nakshatra_index(moon_lon) % 9]
        )


def test_cycle_totals_120_years():
    assert float(VIMSHOTTARI_TOTAL_YEARS) == 120.0
    assert np.isclose(sum(float(y) for y in VIMSHOTTARI_YEARS.values()), 120.0)
