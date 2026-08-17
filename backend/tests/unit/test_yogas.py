"""Unit tests for the classical yogas detected from the D1 chart.

Each yoga is asserted by constructing a whole-sign chart that satisfies
(or violates) exactly the classical condition of that yoga.

The ``_BLANK`` chart (lagna Mesha) is deliberately free of every yoga:
    Sun Mithuna, Moon Dhanus, Mars Simha, Mercury Kumbha,
    Jupiter Mesha (house 1 but neutral), Venus Kanya, Saturn Meena.
"""

from __future__ import annotations

import numpy as np
from app.vedic.dignity import Dignity, assess_dignity
from app.vedic.tables import Graha
from app.vedic.yogas import YogaResult, detect_yogas

#: A full chart with every graha in a sign where no yoga fires.
_BLANK: dict[Graha, np.float64] = {
    Graha.SURYA: np.float64(2 * 30.0 + 10.0),  # Mithuna, house 3
    Graha.CHANDRA: np.float64(8 * 30.0 + 10.0),  # Dhanus, house 9
    Graha.CHEVVAI: np.float64(4 * 30.0 + 20.0),  # Simha (neutral), house 5
    Graha.BUDHA: np.float64(10 * 30.0 + 15.0),  # Kumbha (neutral), house 11
    Graha.GURU: np.float64(0 * 30.0 + 5.0),  # Mesha (neutral), house 1
    Graha.SUKRA: np.float64(5 * 30.0 + 20.0),  # Kanya (neutral), house 6
    Graha.SANI: np.float64(11 * 30.0 + 10.0),  # Meena (neutral), house 12
}


def _result(results: list[YogaResult], name: str) -> YogaResult:
    for result in results:
        if result.name == name:
            return result
    raise AssertionError(f"yoga '{name}' not in results")


def _set(positions: dict[Graha, np.float64], graha: Graha, lon: float) -> dict[Graha, np.float64]:
    updated = dict(positions)
    updated[graha] = np.float64(lon)
    return updated


# ═══════════════════════════════════════════════════════════════════════ #
# Pancha Mahapurusha
# ═══════════════════════════════════════════════════════════════════════ #


def test_blank_chart_has_no_mahapurusha_yogas():
    results = detect_yogas(0, _BLANK)
    for name in ("Ruchaka", "Bhadra", "Hamsa", "Malavya", "Sasa"):
        assert not _result(results, name).present


def test_ruchaka_present_when_mars_strong_in_kendra():
    """Mars in Aries (own sign) with Mesha lagna → kendra house 1."""
    positions = _set(_BLANK, Graha.CHEVVAI, 0 * 30.0 + 20.0)
    results = detect_yogas(0, positions)
    assert _result(results, "Ruchaka").present


def test_ruchaka_absent_when_strong_but_not_kendra():
    """Mars in Aries (own sign) with Vrishabha lagna → Aries is house 12."""
    positions = _set(_BLANK, Graha.CHEVVAI, 0 * 30.0 + 20.0)
    results = detect_yogas(1, positions)
    assert not _result(results, "Ruchaka").present


def test_ruchaka_absent_when_kendra_but_not_strong():
    """Mars in Cancer (kendra house 4 from Mesha lagna) but neutral."""
    positions = _set(_BLANK, Graha.CHEVVAI, 3 * 30.0 + 10.0)
    results = detect_yogas(0, positions)
    assert not _result(results, "Ruchaka").present


def test_sasa_present_when_saturn_exalted_in_kendra():
    """Saturn in Tula (exalted sign) with Tula lagna → kendra house 1."""
    positions = _set(_BLANK, Graha.SANI, 6 * 30.0 + 0.0)
    results = detect_yogas(6, positions)
    assert _result(results, "Sasa").present


def test_bhadra_present_when_mercury_moolatrikona_in_kendra():
    """Mercury moolatrikona in Kanya 16–20° with Kanya lagna."""
    positions = _set(_BLANK, Graha.BUDHA, 5 * 30.0 + 18.0)
    results = detect_yogas(5, positions)
    assert _result(results, "Bhadra").present


# ═══════════════════════════════════════════════════════════════════════ #
# Gajakesari, Budha-Aditya, Chandra-Mangala
# ═══════════════════════════════════════════════════════════════════════ #


def test_gajakesari_present_when_jupiter_in_kendra_from_moon():
    positions = _set(_BLANK, Graha.GURU, 5 * 30.0 + 5.0)  # Kanya = 10th from Dhanus
    results = detect_yogas(0, positions)
    assert _result(results, "Gajakesari").present


def test_gajakesari_absent_when_jupiter_outside_kendra_from_moon():
    positions = _set(_BLANK, Graha.GURU, 1 * 30.0 + 5.0)  # Vrishabha = 6th from Dhanus
    results = detect_yogas(0, positions)
    assert not _result(results, "Gajakesari").present


def test_budha_aditya():
    positions = _set(_BLANK, Graha.BUDHA, 2 * 30.0 + 20.0)  # conjunct Sun in Mithuna
    results = detect_yogas(0, positions)
    assert _result(results, "Budha-Aditya").present
    results = detect_yogas(0, _BLANK)  # Mercury in Kumbha, Sun in Mithuna
    assert not _result(results, "Budha-Aditya").present


def test_chandra_mangala():
    positions = _set(_BLANK, Graha.CHEVVAI, 8 * 30.0 + 15.0)  # conjunct Moon in Dhanus
    results = detect_yogas(0, positions)
    assert _result(results, "Chandra-Mangala").present
    results = detect_yogas(0, _BLANK)
    assert not _result(results, "Chandra-Mangala").present


# ═══════════════════════════════════════════════════════════════════════ #
# Sunapha / Anapha / Durudhara (from the Moon)
# ═══════════════════════════════════════════════════════════════════════ #


def test_sunapha_present_when_planet_in_second_from_moon():
    positions = _set(_BLANK, Graha.BUDHA, 9 * 30.0 + 10.0)  # Makara = 2nd from Dhanus
    results = detect_yogas(0, positions)
    assert _result(results, "Sunapha").present


def test_anapha_present_when_planet_in_twelfth_from_moon():
    positions = _set(_BLANK, Graha.BUDHA, 7 * 30.0 + 10.0)  # Vrischika = 12th from Dhanus
    results = detect_yogas(0, positions)
    assert _result(results, "Anapha").present


def test_durudhara_present_when_both_flanks_occupied():
    positions = dict(_BLANK)
    positions[Graha.BUDHA] = np.float64(9 * 30.0 + 10.0)  # 2nd from Moon
    positions[Graha.SUKRA] = np.float64(7 * 30.0 + 10.0)  # 12th from Moon
    results = detect_yogas(0, positions)
    assert _result(results, "Sunapha").present
    assert _result(results, "Anapha").present
    assert _result(results, "Durudhara").present


def test_durudhara_absent_when_only_one_flank_occupied():
    positions = _set(_BLANK, Graha.BUDHA, 9 * 30.0 + 10.0)
    results = detect_yogas(0, positions)
    assert _result(results, "Sunapha").present
    assert not _result(results, "Durudhara").present


# ═══════════════════════════════════════════════════════════════════════ #
# Kemadruma
# ═══════════════════════════════════════════════════════════════════════ #


def test_kemadruma_present_when_no_planet_near_moon():
    results = detect_yogas(0, _BLANK)
    assert _result(results, "Kemadruma").present


def test_kemadruma_absent_when_sun_in_second_from_moon():
    """The Sun in house 2 from the Moon cancels Kemadruma."""
    positions = _set(_BLANK, Graha.SURYA, 9 * 30.0 + 5.0)  # Makara = 2nd from Dhanus
    results = detect_yogas(0, positions)
    assert not _result(results, "Kemadruma").present


# ═══════════════════════════════════════════════════════════════════════ #
# Vesi / Vasi / Ubhayachari (from the Sun)
# ═══════════════════════════════════════════════════════════════════════ #


def test_vesi_present_when_planet_in_second_from_sun():
    positions = _set(_BLANK, Graha.SANI, 3 * 30.0 + 10.0)  # Karka = 2nd from Mithuna
    results = detect_yogas(0, positions)
    assert _result(results, "Vesi").present


def test_vasi_present_when_planet_in_twelfth_from_sun():
    positions = _set(_BLANK, Graha.SANI, 1 * 30.0 + 10.0)  # Vrishabha = 12th from Mithuna
    results = detect_yogas(0, positions)
    assert _result(results, "Vasi").present


def test_ubhayachari_present_when_both_flanks_of_sun_occupied():
    positions = dict(_BLANK)
    positions[Graha.SANI] = np.float64(3 * 30.0 + 10.0)  # 2nd from Sun
    positions[Graha.BUDHA] = np.float64(1 * 30.0 + 10.0)  # 12th from Sun
    results = detect_yogas(0, positions)
    assert _result(results, "Vesi").present
    assert _result(results, "Vasi").present
    assert _result(results, "Ubhayachari").present


# ═══════════════════════════════════════════════════════════════════════ #
# Reporting
# ═══════════════════════════════════════════════════════════════════════ #


def test_all_supported_yogas_are_reported():
    """detect_yogas returns an entry for every supported yoga, present or not."""
    results = detect_yogas(0, _BLANK)
    names = {
        "Ruchaka",
        "Bhadra",
        "Hamsa",
        "Malavya",
        "Sasa",
        "Gajakesari",
        "Budha-Aditya",
        "Chandra-Mangala",
        "Sunapha",
        "Anapha",
        "Durudhara",
        "Kemadruma",
        "Vesi",
        "Vasi",
        "Ubhayachari",
    }
    assert {result.name for result in results} == names
    for result in results:
        assert isinstance(result, YogaResult)
        assert isinstance(result.present, bool)
        assert result.detail  # human-readable basis present


def test_dignity_seen_by_yoga_detection():
    """The blank chart's Sun (Mithuna) and Mars (Simha) are neutral."""
    assert assess_dignity(Graha.SURYA, _BLANK[Graha.SURYA]).dignity is Dignity.NEUTRAL
    assert assess_dignity(Graha.CHEVVAI, _BLANK[Graha.CHEVVAI]).dignity is Dignity.NEUTRAL
