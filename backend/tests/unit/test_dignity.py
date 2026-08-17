"""Unit tests for graha dignity (docs/south-indian-horoscope.md §3.3).

Exaltation/debilitation points and moolatrikona spans follow Brihat
Parashara Hora Shastra ch. 3; the sign-based exaltation convention and
the modern Rahu/Ketu exaltation signs follow the reference docs.
"""

from __future__ import annotations

import numpy as np
import pytest
from app.vedic.dignity import (
    Dignity,
    assess_dignity,
    get_debilitation_point,
    get_exaltation_point,
)
from app.vedic.tables import Graha


def test_exaltation_points():
    points = {
        Graha.SURYA: (0, 10.0),
        Graha.CHANDRA: (1, 3.0),
        Graha.CHEVVAI: (9, 28.0),
        Graha.BUDHA: (5, 15.0),
        Graha.GURU: (3, 5.0),
        Graha.SUKRA: (11, 27.0),
        Graha.SANI: (6, 20.0),
        Graha.RAHU: (1, 0.0),
        Graha.KETU: (7, 0.0),
    }
    for graha, (rasi_index, degree) in points.items():
        point = get_exaltation_point(graha)
        assert point.rasi_index == rasi_index, graha
        assert np.isclose(float(point.degree_in_sign), degree), graha


def test_debilitation_is_opposite_sign():
    for graha in Graha:
        exaltation = get_exaltation_point(graha)
        debilitation = get_debilitation_point(graha)
        assert debilitation.rasi_index == (exaltation.rasi_index + 6) % 12
        assert np.isclose(
            float(debilitation.degree_in_sign),
            30.0 - float(exaltation.degree_in_sign),
        )


def test_exalted_in_exaltation_sign():
    """Sun in Mesha (any degree) is exalted under the sign convention."""
    assessment = assess_dignity(Graha.SURYA, np.float64(5.0))
    assert assessment.dignity is Dignity.EXALTED
    assert assessment.rasi_index == 0
    assert np.isclose(float(assessment.degree_in_sign), 5.0)


def test_debilitated_in_debilitation_sign():
    """Sun in Tula is debilitated."""
    assessment = assess_dignity(Graha.SURYA, np.float64(180.0 + 15.0))
    assert assessment.dignity is Dignity.DEBILITATED


def test_moolatrikona():
    # Sun in Leo 0–20° → moolatrikona; Leo 20–30° → own sign
    assert assess_dignity(Graha.SURYA, np.float64(120.0 + 10.0)).dignity is Dignity.MOOLATRIKONA
    assert assess_dignity(Graha.SURYA, np.float64(120.0 + 25.0)).dignity is Dignity.OWN_SIGN
    # Mars in Aries 0–12° → moolatrikona; Aries 12–30° → own sign
    assert assess_dignity(Graha.CHEVVAI, np.float64(5.0)).dignity is Dignity.MOOLATRIKONA
    assert assess_dignity(Graha.CHEVVAI, np.float64(20.0)).dignity is Dignity.OWN_SIGN
    # Venus in Libra 0–15° → moolatrikona
    assert assess_dignity(Graha.SUKRA, np.float64(180.0 + 5.0)).dignity is Dignity.MOOLATRIKONA


def test_own_sign():
    assert assess_dignity(Graha.SURYA, np.float64(120.0 + 25.0)).dignity is Dignity.OWN_SIGN
    assert assess_dignity(Graha.CHANDRA, np.float64(90.0 + 10.0)).dignity is Dignity.OWN_SIGN
    assert assess_dignity(Graha.CHEVVAI, np.float64(210.0 + 10.0)).dignity is Dignity.OWN_SIGN
    assert assess_dignity(Graha.BUDHA, np.float64(60.0 + 10.0)).dignity is Dignity.OWN_SIGN
    assert assess_dignity(Graha.GURU, np.float64(240.0 + 20.0)).dignity is Dignity.OWN_SIGN
    assert assess_dignity(Graha.SUKRA, np.float64(30.0 + 20.0)).dignity is Dignity.OWN_SIGN
    assert assess_dignity(Graha.SANI, np.float64(300.0 + 25.0)).dignity is Dignity.OWN_SIGN


def test_neutral():
    assert assess_dignity(Graha.SURYA, np.float64(60.0)).dignity is Dignity.NEUTRAL
    assert assess_dignity(Graha.CHANDRA, np.float64(240.0)).dignity is Dignity.NEUTRAL
    assert assess_dignity(Graha.SUKRA, np.float64(90.0)).dignity is Dignity.NEUTRAL


def test_rahu_ketu_convention():
    """Rahu exalted in Vrishabha, Ketu in Vrischika (modern convention);
    neither has own signs → neutral elsewhere."""
    assert assess_dignity(Graha.RAHU, np.float64(35.0)).dignity is Dignity.EXALTED
    assert assess_dignity(Graha.KETU, np.float64(215.0)).dignity is Dignity.EXALTED
    assert assess_dignity(Graha.RAHU, np.float64(130.0)).dignity is Dignity.NEUTRAL
    assert assess_dignity(Graha.KETU, np.float64(60.0)).dignity is Dignity.NEUTRAL


def test_exaltation_distance():
    assessment = assess_dignity(Graha.SURYA, np.float64(10.0))
    assert np.isclose(float(assessment.distance_from_exaltation_deg), 0.0)
    assessment = assess_dignity(Graha.SURYA, np.float64(5.0))
    assert np.isclose(float(assessment.distance_from_exaltation_deg), 5.0)
    # outside the exaltation sign there is no distance
    assessment = assess_dignity(Graha.SURYA, np.float64(60.0))
    assert assessment.distance_from_exaltation_deg is None


def test_dignity_precedence():
    """Exaltation outranks moolatrikona (Sun at 0° Mesha is exalted, not neutral)."""
    assessment = assess_dignity(Graha.SURYA, np.float64(0.0))
    assert assessment.dignity is Dignity.EXALTED
    # moolatrikona outranks own sign (Mars at 5° Aries)
    assert assess_dignity(Graha.CHEVVAI, np.float64(5.0)).dignity is Dignity.MOOLATRIKONA
    # own sign outranks neutral (Sun at 25° Leo)
    assert assess_dignity(Graha.SURYA, np.float64(145.0)).dignity is Dignity.OWN_SIGN


def test_unknown_graha_rejected():
    with pytest.raises(ValueError):
        get_exaltation_point("NotAGraha")
    with pytest.raises(ValueError):
        get_debilitation_point("NotAGraha")
