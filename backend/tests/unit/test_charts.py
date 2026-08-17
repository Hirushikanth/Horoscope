"""Unit tests for divisional charts (vargas) and vargottama.

The navamsa, dasamsa, dwadasamsa and shashtiamsa follow the sign-nature
counting rule of docs/01 §10 (chara from the sign itself, sthira from
the 9th, dwisvabhava from the 5th); D10 shifts the dual-sign start to
the 7th; D30 uses the odd/even-sign trimsamsa scheme. Every combination
is asserted here, plus the docs' worked example where available.
"""

from __future__ import annotations

import numpy as np
import pytest
from app.vedic.charts import (
    NAVAMSA_SPAN_DEG,
    Varga,
    VargaPosition,
    get_dasamsa_position,
    get_dwadasamsa_position,
    get_graha_vargas,
    get_navamsa_position,
    get_shashtiamsa_position,
    get_sign_nature,
    get_trimsamsa_position,
    get_varga_position,
    is_vargottama,
)
from app.vedic.tables import Graha


def _navamsa_start(rasi_index: int) -> int:
    nature = get_sign_nature(rasi_index)
    if nature == "chara":
        return 0
    if nature == "sthira":
        return 8
    return 4


def _degrees(rasi_index: int, division: int, divisions: int) -> np.float64:
    """Longitude just inside ``division`` of ``rasi_index``."""
    span = np.float64(30.0) / divisions
    return np.float64(rasi_index) * np.float64(30.0) + division * span + 1e-9


# ═══════════════════════════════════════════════════════════════════════ #
# Sign natures
# ═══════════════════════════════════════════════════════════════════════ #


def test_sign_natures():
    assert get_sign_nature(0) == "chara"  # Mesha
    assert get_sign_nature(3) == "chara"  # Karka
    assert get_sign_nature(6) == "chara"  # Tula
    assert get_sign_nature(9) == "chara"  # Makara
    assert get_sign_nature(1) == "sthira"  # Vrishabha
    assert get_sign_nature(4) == "sthira"  # Simha
    assert get_sign_nature(7) == "sthira"  # Vrischika
    assert get_sign_nature(10) == "sthira"  # Kumbha
    assert get_sign_nature(2) == "dwisvabhava"  # Mithuna
    assert get_sign_nature(5) == "dwisvabhava"  # Kanya
    assert get_sign_nature(8) == "dwisvabhava"  # Dhanus
    assert get_sign_nature(11) == "dwisvabhava"  # Meena
    with pytest.raises(ValueError):
        get_sign_nature(12)


# ═══════════════════════════════════════════════════════════════════════ #
# Navamsa (D9) — all 108 divisions
# ═══════════════════════════════════════════════════════════════════════ #


def test_navamsa_all_108_combinations():
    for rasi_index in range(12):
        start = _navamsa_start(rasi_index)
        for division in range(9):
            lon = _degrees(rasi_index, division, 9)
            position = get_navamsa_position(lon)
            expected_sign = (rasi_index + start + division) % 12
            assert position.rasi_index == expected_sign, (rasi_index, division)
            assert position.division_index == division, (rasi_index, division)
            assert position.varga is Varga.NAVAMSA


def test_navamsa_known_spots():
    # 10° Mesha (rasi 0, division 2) — chara, starts from itself → Mithuna
    assert get_navamsa_position(np.float64(10.0)).rasi_index == 2
    # 0° Karka (rasi 3, division 0) — chara → Karka
    assert get_navamsa_position(np.float64(90.0)).rasi_index == 3
    # 0° Vrishabha (rasi 1, division 0) — sthira starts from 9th → Makara
    assert get_navamsa_position(np.float64(30.0)).rasi_index == 9
    # 0° Mithuna (rasi 2, division 0) — dual starts from 5th → Tula
    assert get_navamsa_position(np.float64(60.0)).rasi_index == 6
    # 359° — last navamsa of Meena: rasi 11, division 8, start 4 → (11+4+8)%12 = 11
    assert get_navamsa_position(np.float64(359.0)).rasi_index == 11
    assert get_navamsa_position(np.float64(359.0)).division_index == 8


# ═══════════════════════════════════════════════════════════════════════ #
# Dasamsa (D10)
# ═══════════════════════════════════════════════════════════════════════ #


def test_dasamsa_all_120_divisions():
    for rasi_index in range(12):
        nature = get_sign_nature(rasi_index)
        start = 0 if nature == "chara" else (8 if nature == "sthira" else 6)
        for division in range(10):
            lon = _degrees(rasi_index, division, 10)
            position = get_dasamsa_position(lon)
            assert position.rasi_index == (rasi_index + start + division) % 12
            assert position.division_index == division
            assert position.varga is Varga.DASAMSA


def test_dasamsa_known_spots():
    # 0° Mithuna (dual) → starts from 7th (rasi 8) → Dhanus
    assert get_dasamsa_position(np.float64(60.0)).rasi_index == 8
    # 0° Vrishabha (fixed) → starts from 9th → Makara
    assert get_dasamsa_position(np.float64(30.0)).rasi_index == 9


# ═══════════════════════════════════════════════════════════════════════ #
# Dwadasamsa (D12)
# ═══════════════════════════════════════════════════════════════════════ #


def test_dwadasamsa_all_144_divisions():
    for rasi_index in range(12):
        start = _navamsa_start(rasi_index)
        for division in range(12):
            lon = _degrees(rasi_index, division, 12)
            position = get_dwadasamsa_position(lon)
            assert position.rasi_index == (rasi_index + start + division) % 12
            assert position.division_index == division
            assert position.varga is Varga.DWADASAMSA


def test_dwadasamsa_known_spots():
    # 0° Vrishabha (fixed) → starts from 9th → Makara
    assert get_dwadasamsa_position(np.float64(30.0)).rasi_index == 9
    # 5° Vrishabha — division 2 → (1 + 8 + 2) % 12 = 11 Meena
    assert get_dwadasamsa_position(np.float64(35.0)).rasi_index == 11


# ═══════════════════════════════════════════════════════════════════════ #
# Trimsamsa (D30) — odd/even-sign scheme
# ═══════════════════════════════════════════════════════════════════════ #

ODD_SEQUENCE = (0, 2, 4, 6, 8, 10)
EVEN_SEQUENCE = (1, 3, 5, 7, 9, 11)


def test_trimsamsa_all_72_divisions():
    for rasi_index in range(12):
        sequence = ODD_SEQUENCE if rasi_index % 2 == 0 else EVEN_SEQUENCE
        position_in_sequence = sequence.index(rasi_index)
        for division in range(6):
            lon = _degrees(rasi_index, division, 6)
            position = get_trimsamsa_position(lon)
            assert position.rasi_index == sequence[(position_in_sequence + division) % 6]
            assert position.division_index == division
            assert position.varga is Varga.TRIMSAMSA


def test_trimsamsa_known_spots():
    # 0° Mesha (odd) → Mesha; 25° Mesha (division 5) → (0+5 in odd seq) = 10 Kumbha
    assert get_trimsamsa_position(np.float64(0.0)).rasi_index == 0
    assert get_trimsamsa_position(np.float64(25.0)).rasi_index == 10
    # 0° Vrishabha (even) → Vrishabha; 25° Vrishabha → 11 Meena
    assert get_trimsamsa_position(np.float64(30.0)).rasi_index == 1
    assert get_trimsamsa_position(np.float64(55.0)).rasi_index == 11


# ═══════════════════════════════════════════════════════════════════════ #
# Shashtiamsa (D60)
# ═══════════════════════════════════════════════════════════════════════ #


def test_shashtiamsa_all_720_divisions():
    for rasi_index in range(12):
        start = _navamsa_start(rasi_index)
        for division in range(60):
            lon = _degrees(rasi_index, division, 60)
            position = get_shashtiamsa_position(lon)
            assert position.rasi_index == (rasi_index + start + division) % 12
            assert position.division_index == division
            assert position.varga is Varga.SHASHTIAMSA


def test_shashtiamsa_known_spots():
    # 0° Mesha (chara) → Mesha
    assert get_shashtiamsa_position(np.float64(0.0)).rasi_index == 0
    # 29°59′ Mesha — division 59 → (0 + 0 + 59) % 12 = 11 Meena
    assert get_shashtiamsa_position(np.float64(29.95)).rasi_index == 11


# ═══════════════════════════════════════════════════════════════════════ #
# Generic dispatcher + vargottama
# ═══════════════════════════════════════════════════════════════════════ #


def test_get_varga_position_dispatcher():
    lon = np.float64(75.0)
    assert get_varga_position(lon, Varga.RASI).varga is Varga.RASI
    assert get_varga_position(lon, Varga.NAVAMSA) == get_navamsa_position(lon)
    assert get_varga_position(lon, Varga.DASAMSA) == get_dasamsa_position(lon)
    assert get_varga_position(lon, Varga.DWADASAMSA) == get_dwadasamsa_position(lon)
    assert get_varga_position(lon, Varga.TRIMSAMSA) == get_trimsamsa_position(lon)
    assert get_varga_position(lon, Varga.SHASHTIAMSA) == get_shashtiamsa_position(lon)
    assert isinstance(get_varga_position(lon, Varga.RASI), VargaPosition)


def test_vargottama_known_spots():
    # Simha 13°20′ — navamsa division 4: (4 + 8 + 4) % 12 = 4 Simha → vargottama
    vargottama_lon = np.float64(4 * 30.0 + 4 * NAVAMSA_SPAN_DEG)
    assert is_vargottama(vargottama_lon)
    # Simha 0° — navamsa division 0: (4 + 8 + 0) % 12 = 0 Mesha → not vargottama
    assert not is_vargottama(np.float64(120.0 + 1e-9))


def test_get_graha_vargas():
    positions = {graha: np.float64(index * 3.3 + 1.1) for index, graha in enumerate(Graha)}
    result = get_graha_vargas(positions)
    assert set(result) == set(Graha)
    for _graha, vargas in result.items():
        assert set(vargas) == {
            Varga.NAVAMSA,
            Varga.DASAMSA,
            Varga.DWADASAMSA,
            Varga.TRIMSAMSA,
            Varga.SHASHTIAMSA,
        }
        for varga, position in vargas.items():
            assert position.varga is varga
            assert 0 <= position.rasi_index <= 11
