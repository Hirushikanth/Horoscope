"""Unit tests for whole-sign bhavas (docs/01 §8, docs/south-indian-horoscope.md §2.2)."""

from __future__ import annotations

import numpy as np
import pytest
from app.vedic.bhavas import (
    Bhava,
    get_bhava_of_longitude,
    get_house_number,
    get_whole_sign_bhavas,
    house_relations,
)


def test_house_number_counts_clockwise_from_lagna():
    # lagna = Mesha: Mesha is house 1, Vrishabha 2, … Meena 12
    assert get_house_number(0, 0) == 1
    assert get_house_number(0, 1) == 2
    assert get_house_number(0, 11) == 12
    # lagna = Kanya (5): Kanya 1, Tula 2, Simha 12
    assert get_house_number(5, 5) == 1
    assert get_house_number(5, 6) == 2
    assert get_house_number(5, 4) == 12
    # wrap-around: lagna = Vrischika (7), Mesha is house 6
    assert get_house_number(7, 0) == 6


def test_house_number_rejects_out_of_range():
    with pytest.raises(ValueError):
        get_house_number(12, 0)
    with pytest.raises(ValueError):
        get_house_number(0, 12)
    with pytest.raises(ValueError):
        get_house_number(-1, 0)


def test_bhava_of_longitude():
    # lagna Mesha (0): longitude 120° (Simha) is house 5
    assert get_bhava_of_longitude(0, np.float64(120.0)) == 5
    # lagna Mesha: 359° (Meena) is house 12
    assert get_bhava_of_longitude(0, np.float64(359.0)) == 12
    # lagna Kanya (5): 30° (Vrishabha) is house 9
    assert get_bhava_of_longitude(5, np.float64(30.0)) == 9


def test_whole_sign_bhavas():
    lagna = 5  # Kanya
    bhavas = get_whole_sign_bhavas(lagna)
    assert len(bhavas) == 12
    for index, bhava in enumerate(bhavas):
        assert isinstance(bhava, Bhava)
        assert bhava.house_number == index + 1
        assert bhava.rasi_index == (lagna + index) % 12
        assert bhava.lord is not None
    # house 1 is the lagna sign itself
    assert bhavas[0].rasi_index == 5


def test_house_relations():
    assert house_relations(1) == {"kendra": True, "trikona": True, "dusthana": False}
    assert house_relations(5) == {"kendra": False, "trikona": True, "dusthana": False}
    assert house_relations(6) == {"kendra": False, "trikona": False, "dusthana": True}
    assert house_relations(10) == {"kendra": True, "trikona": False, "dusthana": False}
    assert house_relations(2) == {"kendra": False, "trikona": False, "dusthana": False}
