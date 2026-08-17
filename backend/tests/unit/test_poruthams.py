"""Unit tests for the eleven Kalyana Porutham checks (Phase D, M4).

Every rule of docs/02 is asserted here, table-driven where possible:

    - §1 Dina: the 27×27 nakshatra counts against the Tara remainders,
      plus the Aega Nakshatram Uthamam/Madhyamam lists.
    - §2 Gana: all 3×3 gana combinations.
    - §3 Mahendra: all 27 counts against {4,7,10,13,16,19,22,25}.
    - §4 Stree Deergha: all 27 counts against the 13/7 thresholds.
    - §5 Yoni: same-yoni, enemy-pair and non-enemy pairs.
    - §6 Rasi: all 12×12 counts, Sashtashtaka, and the Eka Rasi
      ordering exception with its exemption list.
    - §7 Rasi Athipathi: same-lord / mutual-friend / mixed / enemy cases.
    - §8 Vashya: same-group, food-chain and half-sign (Dhanus, Makara).
    - §9 Rajju: same-group dosha across all 27×27 pairs.
    - §10 Vedha: all 13 pairs + Chitra (and all 27×27).
    - Nadi: same/different across all 27×27 pairs.
"""

from __future__ import annotations

import numpy as np
import pytest
from app.matching.poruthams import (
    AEGA_NAKSHATRAM_MADHYAMAM,
    AEGA_NAKSHATRAM_UTHAMAM,
    EKA_RASI_EXEMPT_NAKSHATRAS,
    MAHENDRA_COUNTS,
    MatchingInput,
    PoruthamResult,
    dina_porutham,
    gana_porutham,
    mahendra_porutham,
    nadi_porutham,
    rajju_porutham,
    rasi_athipathi_porutham,
    rasi_porutham,
    stree_deergha_porutham,
    vashya_porutham,
    vedha_porutham,
    yoni_porutham,
)
from app.vedic.nakshatra import (
    NAKSHATRA_CLASSIFICATION,
    VEDHA_PAIRS,
    Gana,
    get_nakshatra_gana,
    get_nakshatra_nadi,
    get_nakshatra_rajju,
    get_nakshatra_yoni,
)
from app.vedic.rashi import (
    PANCHADHA_MAITRI,
    RASI_LORDS,
    MaitriRelation,
    VashyaGroup,
    get_vashya_group,
)
from app.vedic.tables import Graha


def make_input(
    nakshatra_index: int,
    *,
    pada: int = 1,
    rasi_index: int = 0,
    degree_in_sign: float = 15.0,
    chevvai_dosham: bool = False,
) -> MatchingInput:
    """Convenience constructor — a MatchingInput with only the fields the
    check under test cares about populated."""
    return MatchingInput(
        nakshatra_index=nakshatra_index,
        pada=pada,
        rasi_index=rasi_index,
        moon_degree_in_sign=np.float64(degree_in_sign),
        chevvai_dosham=chevvai_dosham,
    )


def _count(bride: int, groom: int) -> int:
    """Inclusive bride→groom nakshatra count (the docs' counting)."""
    return (groom - bride) % 27 + 1


# ═══════════════════════════════════════════════════════════════════════ #
# §1 — Dina Porutham
# ═══════════════════════════════════════════════════════════════════════ #

#: Counts whose Tara remainder is auspicious — docs/02 §1 lists 2, 4, 6,
#: 8, 9, 11, 13, 15, 18, 20, 24, 26 (the mathematical rule adds 27).
AUSPICIOUS_COUNTS = {c for c in range(1, 28) if (c % 9 or 9) in {2, 4, 6, 8, 9}}
#: Counts landing on Vipat / Pratyak / Naidhana (remainders 3, 5, 7).
IN_AUSPICIOUS_COUNTS = {c for c in range(1, 28) if (c % 9 or 9) in {3, 5, 7}}


@pytest.mark.parametrize("count", sorted(AUSPICIOUS_COUNTS))
def test_dina_auspicious_tara_counts(count: int) -> None:
    # Count from Ashwini (0) to (count-1); 1 is handled by Aega tests.
    if count == 1:
        return
    result = dina_porutham(make_input(0), make_input(count - 1))
    assert result.result is PoruthamResult.UTHAMAM, f"count {count}"
    assert result.detail["count"] == count


@pytest.mark.parametrize("count", sorted(IN_AUSPICIOUS_COUNTS))
def test_dina_inauspicious_tara_counts(count: int) -> None:
    if count == 1:
        return
    result = dina_porutham(make_input(0), make_input(count - 1))
    assert result.result is PoruthamResult.ATHAMAM, f"count {count}"


def test_dina_janma_counts_are_madhyamam() -> None:
    """Counts 10 and 19 land on Janma (remainder 1), which the docs call
    neutral — scored Madhyamam pending astrologer judgement."""
    assert _count(0, 9) == 10
    assert _count(0, 18) == 19
    for count in (10, 19):
        result = dina_porutham(make_input(0), make_input(count - 1))
        assert result.result is PoruthamResult.MADHYAMAM
        assert result.detail["tara"] == "Janma"


@pytest.mark.parametrize("nakshatra", sorted(AEGA_NAKSHATRAM_UTHAMAM))
def test_dina_aega_nakshatram_uthamam_list(nakshatra: int) -> None:
    """Same nakshatra pairs on the docs' Uthamam list (Rohini, Ardra,
    Pushya, Magha, Hasta, Shravana)."""
    result = dina_porutham(make_input(nakshatra), make_input(nakshatra))
    assert result.result is PoruthamResult.UTHAMAM, f"nakshatra {nakshatra}"


@pytest.mark.parametrize("nakshatra", sorted(AEGA_NAKSHATRAM_MADHYAMAM))
def test_dina_aega_nakshatram_madhyamam_list(nakshatra: int) -> None:
    result = dina_porutham(make_input(nakshatra), make_input(nakshatra))
    assert result.result is PoruthamResult.MADHYAMAM, f"nakshatra {nakshatra}"


@pytest.mark.parametrize("nakshatra", [n for n in range(27) if n not in AEGA_NAKSHATRAM_UTHAMAM])
def test_dina_aega_nakshatram_remaining_are_conservative(nakshatra: int) -> None:
    """Remaining same-star pairs are 'weighed case by case' in the docs;
    they must never be scored Uthamam."""
    result = dina_porutham(make_input(nakshatra), make_input(nakshatra))
    assert result.result is not PoruthamResult.UTHAMAM


def test_dina_count_matches_docs_example_list() -> None:
    """The docs' explicit example list of good counts."""
    for count in (2, 4, 6, 8, 9, 11, 13, 15, 18, 20, 24, 26):
        assert dina_porutham(make_input(0), make_input(count - 1)).result is PoruthamResult.UTHAMAM


# ═══════════════════════════════════════════════════════════════════════ #
# §2 — Gana Porutham
# ═══════════════════════════════════════════════════════════════════════ #

# (bride_gana, groom_gana) → expected result — docs/02 §2.
GANA_EXPECTED: dict[tuple[Gana, Gana], PoruthamResult] = {
    (Gana.DEVA, Gana.DEVA): PoruthamResult.UTHAMAM,
    (Gana.MANUSHYA, Gana.MANUSHYA): PoruthamResult.UTHAMAM,
    (Gana.DEVA, Gana.MANUSHYA): PoruthamResult.UTHAMAM,
    (Gana.MANUSHYA, Gana.DEVA): PoruthamResult.UTHAMAM,
    (Gana.MANUSHYA, Gana.RAKSHASA): PoruthamResult.MADHYAMAM,
    (Gana.RAKSHASA, Gana.MANUSHYA): PoruthamResult.MADHYAMAM,
    (Gana.RAKSHASA, Gana.RAKSHASA): PoruthamResult.MADHYAMAM,
    (Gana.DEVA, Gana.RAKSHASA): PoruthamResult.ATHAMAM,
    (Gana.RAKSHASA, Gana.DEVA): PoruthamResult.ATHAMAM,
}

#: One nakshatra per gana to drive the 3×3 matrix.
_NAKSHATRA_OF_GANA = {Gana.DEVA: 0, Gana.MANUSHYA: 1, Gana.RAKSHASA: 2}


@pytest.mark.parametrize("pair", sorted(GANA_EXPECTED, key=lambda p: (p[0].value, p[1].value)))
def test_gana_matrix(pair: tuple[Gana, Gana]) -> None:
    result = gana_porutham(
        make_input(_NAKSHATRA_OF_GANA[pair[0]]), make_input(_NAKSHATRA_OF_GANA[pair[1]])
    )
    assert result.result is GANA_EXPECTED[pair], pair


def test_gana_classification_consistency() -> None:
    """The gana table used by the check matches docs/02 §2 for all 27."""

    deva = {0, 4, 6, 7, 12, 14, 16, 21, 26}  # Ashwini..Revati (docs §2)
    for idx in range(27):
        expected = (
            Gana.DEVA
            if idx in deva
            else Gana.MANUSHYA
            if idx in {1, 3, 5, 10, 11, 19, 20, 24, 25}
            else Gana.RAKSHASA
        )
        assert get_nakshatra_gana(idx) is expected, idx


# ═══════════════════════════════════════════════════════════════════════ #
# §3 — Mahendra Porutham
# ═══════════════════════════════════════════════════════════════════════ #


@pytest.mark.parametrize("count", range(1, 28))
def test_mahendra_all_counts(count: int) -> None:
    result = mahendra_porutham(make_input(0), make_input(count - 1))
    expected = PoruthamResult.UTHAMAM if count in MAHENDRA_COUNTS else PoruthamResult.ATHAMAM
    assert result.result is expected, f"count {count}"


# ═══════════════════════════════════════════════════════════════════════ #
# §4 — Stree Deergha Porutham
# ═══════════════════════════════════════════════════════════════════════ #


@pytest.mark.parametrize("count", range(1, 28))
def test_stree_deergha_all_counts(count: int) -> None:
    result = stree_deergha_porutham(make_input(0), make_input(count - 1))
    if count >= 13:
        expected = PoruthamResult.UTHAMAM
    elif count >= 7:
        expected = PoruthamResult.MADHYAMAM
    else:
        expected = PoruthamResult.ATHAMAM
    assert result.result is expected, f"count {count}"


# ═══════════════════════════════════════════════════════════════════════ #
# §5 — Yoni Porutham
# ═══════════════════════════════════════════════════════════════════════ #


def test_yoni_same_yoni_opposite_gender_is_uthamam() -> None:
    # Ashwini = Horse ♂, Shatabhisha = Horse ♀ → the ideal match.
    result = yoni_porutham(make_input(0), make_input(23))
    assert result.result is PoruthamResult.UTHAMAM
    assert result.detail["bride_yoni"] == "horse"
    assert result.detail["groom_yoni"] == "horse"


#: The seven enemy yoni pairs — docs/02 §5 (one nakshatra per yoni).
YONI_ENEMY_NAKSHATRA_PAIRS = [
    (11, 13),  # Cow (Uttara Phalguni ♂) ↔ Tiger (Chitra ♀)
    (0, 14),  # Horse (Ashwini ♂) ↔ Buffalo (Swati ♂)
    (26, 22),  # Elephant (Revati ♂) ↔ Lion (Dhanishtha ♀)
    (5, 16),  # Dog (Ardra ♀) ↔ Deer (Anuradha ♀)
    (20, 3),  # Mongoose (Uttara Ashadha ♂) ↔ Serpent (Rohini ♂)
    (8, 9),  # Cat (Ashlesha ♂) ↔ Rat (Magha ♂)
    (21, 7),  # Monkey (Shravana ♀) ↔ Goat (Pushya ♂)
]


@pytest.mark.parametrize("bride,groom", YONI_ENEMY_NAKSHATRA_PAIRS)
def test_yoni_enemy_pairs_are_athamam(bride: int, groom: int) -> None:
    result = yoni_porutham(make_input(bride), make_input(groom))
    assert result.result is PoruthamResult.ATHAMAM
    assert result.detail["enemy_pair"] is True


@pytest.mark.parametrize("bride,groom", YONI_ENEMY_NAKSHATRA_PAIRS)
def test_yoni_enemy_pairs_are_symmetric(bride: int, groom: int) -> None:
    assert yoni_porutham(make_input(groom), make_input(bride)).result is PoruthamResult.ATHAMAM


def test_yoni_different_non_enemy_is_madhyamam() -> None:
    # Horse (Ashwini) vs Elephant (Revati) — different, not enemies.
    result = yoni_porutham(make_input(0), make_input(26))
    assert result.result is PoruthamResult.MADHYAMAM
    assert result.detail["enemy_pair"] is False


def test_yoni_exhaustive_enemy_detection() -> None:
    """Every same-yoni pair in the 27 nakshatras is opposite-gendered and
    must score Uthamam; every non-enemy different-yoni pair Madhyamam;
    every enemy pair Athamam."""
    from app.vedic.nakshatra import yonis_are_enemies

    for bride in range(27):
        for groom in range(27):
            result = yoni_porutham(make_input(bride), make_input(groom))
            b_yoni = get_nakshatra_yoni(bride)
            g_yoni = get_nakshatra_yoni(groom)
            if bride == groom:
                continue  # same star — the check's branch is per docs §5
            if b_yoni.yoni is g_yoni.yoni:
                assert result.result is PoruthamResult.UTHAMAM, (bride, groom)
            elif yonis_are_enemies(b_yoni.yoni, g_yoni.yoni):
                assert result.result is PoruthamResult.ATHAMAM, (bride, groom)
            else:
                assert result.result is PoruthamResult.MADHYAMAM, (bride, groom)


# ═══════════════════════════════════════════════════════════════════════ #
# §6 — Rasi Porutham
# ═══════════════════════════════════════════════════════════════════════ #


@pytest.mark.parametrize("rasi_count", range(1, 13))
def test_rasi_all_counts(rasi_count: int) -> None:
    result = rasi_porutham(
        make_input(0, rasi_index=0), make_input(0, rasi_index=(rasi_count - 1) % 12)
    )
    good = rasi_count in {1, 3, 4, 5, 7, 9, 10, 11}
    # count 1 (same rasi, same nakshatra) has no ordering violation.
    expected = PoruthamResult.UTHAMAM if good else PoruthamResult.ATHAMAM
    assert result.result is expected, f"rasi count {rasi_count}"


def test_rasi_sashtashtaka_is_athamam() -> None:
    for count in (6, 8):
        result = rasi_porutham(
            make_input(0, rasi_index=0), make_input(0, rasi_index=(count - 1) % 12)
        )
        assert result.result is PoruthamResult.ATHAMAM
        assert result.detail["sashtashtaka"] is True


def test_rasi_seventh_is_best() -> None:
    result = rasi_porutham(make_input(0, rasi_index=0), make_input(0, rasi_index=6))
    assert result.result is PoruthamResult.UTHAMAM
    assert result.detail["count"] == 7


# Mesha = rasi 0 contains Ashwini(0), Bharani(1), Krittika(2).
def test_rasi_eka_rasi_ordering_violation_is_athamam() -> None:
    # Bride Bharani before groom Krittika in Mesha; Bharani not exempt.
    result = rasi_porutham(make_input(1, rasi_index=0), make_input(2, rasi_index=0))
    assert result.result is PoruthamResult.ATHAMAM
    assert result.detail["eka_rasi"] is True


def test_rasi_eka_rasi_bride_not_before_groom_is_uthamam() -> None:
    # Bride Krittika, groom Ashwini — bride's star after the groom's.
    result = rasi_porutham(make_input(2, rasi_index=0), make_input(0, rasi_index=0))
    assert result.result is PoruthamResult.UTHAMAM


def test_rasi_eka_rasi_exempt_nakshatras_waive_ordering() -> None:
    """When the bride's star is on the exemption list, her star falling
    before the groom's within the shared rasi is waived (Uthamam)."""
    # Nakshatras fully contained in each rasi (indices; boundary stars
    # that straddle rasis are excluded for simplicity).
    rasi_of: dict[int, set[int]] = {
        0: {0, 1, 2},  # Mesha: Ashwini, Bharani, Krittika
        1: {3, 4},  # Vrishabha: Rohini, Mrigashira
        2: {5, 6},  # Mithuna: Ardra, Punarvasu
        3: {7, 8},  # Karka: Pushya, Ashlesha
        4: {9, 10},  # Simha: Magha, P.Phalguni
        5: {11, 12},  # Kanya: U.Phalguni, Hasta
        6: {13, 14},  # Tula: Chitra, Swati
        7: {15, 16},  # Vrischika: Vishakha, Anuradha
        8: {17, 18},  # Dhanus: Jyeshtha, Mula
        9: {19, 20},  # Makara: P.Ashadha, U.Ashadha
        10: {21, 22},  # Kumbha: Shravana, Dhanishtha
        11: {23, 24},  # Meena: P.Bhadrapada, U.Bhadrapada
    }
    tested = 0
    for exempt in EKA_RASI_EXEMPT_NAKSHATRAS:
        for rasi, stars in rasi_of.items():
            if exempt not in stars:
                continue
            later = [s for s in stars if s > exempt]
            if not later:
                continue  # the star is last in its rasi — ordering cannot
                # be violated by a groom in the same rasi
            groom = min(later)
            result = rasi_porutham(
                make_input(exempt, rasi_index=rasi), make_input(groom, rasi_index=rasi)
            )
            assert result.result is PoruthamResult.UTHAMAM, (exempt, rasi)
            tested += 1
    assert tested == 5  # Ashwini, Rohini, Magha, P.Ashadha, Shatabhisha
    # Krittika, Hasta and Swati are the last stars of their rasis, so the
    # ordering restriction can never be violated for them.


def test_rasi_eka_rasi_non_exempt_ordering_violation() -> None:
    # Bride Bharani before groom Krittika in Mesha (Bharani not exempt).
    result = rasi_porutham(make_input(1, rasi_index=0), make_input(2, rasi_index=0))
    assert result.result is PoruthamResult.ATHAMAM


# ═══════════════════════════════════════════════════════════════════════ #
# §7 — Rasi Athipathi Porutham
# ═══════════════════════════════════════════════════════════════════════ #


def test_rasi_athipathi_same_lord_is_uthamam() -> None:
    # Mesha (Mars) and Vrischika (Mars) — the same graha rules both.
    result = rasi_athipathi_porutham(make_input(0, rasi_index=0), make_input(0, rasi_index=7))
    assert result.result is PoruthamResult.UTHAMAM
    assert result.detail["bride_lord"] == "Mars"
    assert result.detail["groom_lord"] == "Mars"


def test_rasi_athipathi_mutual_friends_is_uthamam() -> None:
    # Simha (Sun) and Karka (Moon) — mutual friends in the Maitri table.
    result = rasi_athipathi_porutham(make_input(0, rasi_index=4), make_input(0, rasi_index=3))
    assert result.result is PoruthamResult.UTHAMAM
    assert result.detail["relationship"] == "friend"


def test_rasi_athipathi_mutual_enemies_is_athamam() -> None:
    # Simha (Sun) and Makara (Saturn) — mutual enemies.
    result = rasi_athipathi_porutham(make_input(0, rasi_index=4), make_input(0, rasi_index=9))
    assert result.result is PoruthamResult.ATHAMAM
    assert result.detail["relationship"] == "enemy"


def test_rasi_athipathi_mixed_is_madhyamam() -> None:
    # Karka (Moon) and Mithuna (Mercury): Moon→Mercury friend, Mercury→Moon enemy.
    result = rasi_athipathi_porutham(make_input(0, rasi_index=3), make_input(0, rasi_index=2))
    assert result.result is PoruthamResult.MADHYAMAM
    assert result.detail["relationship"] == "neutral"


def test_rasi_athipathi_exhaustive_matrix() -> None:
    """All 12×12 rasi pairs against the Panchadha Maitri table directly."""
    for bride in range(12):
        for groom in range(12):
            result = rasi_athipathi_porutham(
                make_input(0, rasi_index=bride), make_input(0, rasi_index=groom)
            )
            b_lord = RASI_LORDS[bride]
            g_lord = RASI_LORDS[groom]
            if b_lord is g_lord:
                expected = PoruthamResult.UTHAMAM
            else:
                b_toward_g = _relation(b_lord, g_lord)
                g_toward_b = _relation(g_lord, b_lord)
                if b_toward_g is MaitriRelation.FRIEND and g_toward_b is MaitriRelation.FRIEND:
                    expected = PoruthamResult.UTHAMAM
                elif b_toward_g is MaitriRelation.ENEMY and g_toward_b is MaitriRelation.ENEMY:
                    expected = PoruthamResult.ATHAMAM
                else:
                    expected = PoruthamResult.MADHYAMAM
            assert result.result is expected, (bride, groom)


def _relation(lord: Graha, other: Graha) -> MaitriRelation:
    row = PANCHADHA_MAITRI[lord]
    if other in row[MaitriRelation.FRIEND]:
        return MaitriRelation.FRIEND
    if other in row[MaitriRelation.ENEMY]:
        return MaitriRelation.ENEMY
    return MaitriRelation.NEUTRAL


# ═══════════════════════════════════════════════════════════════════════ #
# §8 — Vashya Porutham
# ═══════════════════════════════════════════════════════════════════════ #


def test_vashya_same_group_is_uthamam() -> None:
    # Mesha + Vrishabha — both Chatushpada.
    result = vashya_porutham(make_input(0, rasi_index=0), make_input(0, rasi_index=1))
    assert result.result is PoruthamResult.UTHAMAM


def test_vashya_jalachara_manava_food_chain_is_athamam() -> None:
    # Karka (Jalachara) ↔ Mithuna (Manava).
    result = vashya_porutham(make_input(0, rasi_index=3), make_input(0, rasi_index=2))
    assert result.result is PoruthamResult.ATHAMAM
    assert result.detail["food_chain"] is True


def test_vashya_chatushpada_vanachara_food_chain_is_athamam() -> None:
    # Vrishabha (Chatushpada) ↔ Simha (Vanachara).
    result = vashya_porutham(make_input(0, rasi_index=1), make_input(0, rasi_index=4))
    assert result.result is PoruthamResult.ATHAMAM


def test_vashya_other_groups_are_madhyamam() -> None:
    # Vrishchika (Keeta) ↔ Mithuna (Manava).
    result = vashya_porutham(make_input(0, rasi_index=7), make_input(0, rasi_index=2))
    assert result.result is PoruthamResult.MADHYAMAM


def test_vashya_half_sign_dhanus_degree_switch() -> None:
    # Dhanus 5° = Manava, Dhanus 20° = Chatushpada (docs/02 §8).
    assert get_vashya_group(8, np.float64(5.0)) is VashyaGroup.MANAVA
    assert get_vashya_group(8, np.float64(20.0)) is VashyaGroup.CHATUSHPADA
    # Dhanus(Manava half) with Karka (Jalachara) → food chain.
    result = vashya_porutham(
        make_input(0, rasi_index=8, degree_in_sign=5.0), make_input(0, rasi_index=3)
    )
    assert result.result is PoruthamResult.ATHAMAM
    # Dhanus(Chatushpada half) with Mesha (Chatushpada) → same group.
    result = vashya_porutham(
        make_input(0, rasi_index=8, degree_in_sign=20.0), make_input(0, rasi_index=0)
    )
    assert result.result is PoruthamResult.UTHAMAM


def test_vashya_half_sign_makara_degree_switch() -> None:
    # Makara 5° = Chatushpada, Makara 20° = Jalachara (docs/02 §8).
    assert get_vashya_group(9, np.float64(5.0)) is VashyaGroup.CHATUSHPADA
    assert get_vashya_group(9, np.float64(20.0)) is VashyaGroup.JALACHARA


# ═══════════════════════════════════════════════════════════════════════ #
# §9 — Rajju Porutham (Tamil grouping)
# ═══════════════════════════════════════════════════════════════════════ #


@pytest.mark.parametrize("bride", range(27))
def test_rajju_exhaustive(bride: int) -> None:
    for groom in range(27):
        result = rajju_porutham(make_input(bride), make_input(groom))
        same = get_nakshatra_rajju(bride) is get_nakshatra_rajju(groom)
        expected = PoruthamResult.ATHAMAM if same else PoruthamResult.UTHAMAM
        assert result.result is expected, (bride, groom)


#: docs/02 §9 Tamil groupings — (nakshatra index, rajju body part).
RAJJU_BODY_PARTS: dict[str, list[int]] = {
    "siro": [13, 4, 22],  # Chitra, Mrigashira, Dhanishtha
    "kantha": [3, 5, 14, 12, 21, 23],  # Rohini, Ardra, Swati, Hasta, Shravana, Shatabhisha
    "nabhi": [
        2,
        6,
        11,
        15,
        24,
        20,
    ],  # Krittika, Punarvasu, U.Phalguni, Vishakha, P.Bhadrapada, U.Ashadha
    "kati": [
        1,
        7,
        10,
        16,
        25,
        19,
    ],  # Bharani, Pushya, P.Phalguni, Anuradha, U.Bhadrapada, P.Ashadha
    "pada": [0, 8, 9, 18, 17, 26],  # Ashwini, Ashlesha, Magha, Mula, Jyeshtha, Revati
}


def test_rajju_grouping_matches_docs_table() -> None:
    for body_part, stars in RAJJU_BODY_PARTS.items():
        for star in stars:
            assert get_nakshatra_rajju(star).value == body_part, star


# ═══════════════════════════════════════════════════════════════════════ #
# §10 — Vedha Porutham
# ═══════════════════════════════════════════════════════════════════════ #


def test_vedha_exhaustive() -> None:
    """All 13 pairs from the docs, plus Chitra which has no partner."""
    for bride in range(27):
        for groom in range(27):
            result = vedha_porutham(make_input(bride), make_input(groom))
            if bride == groom:
                continue
            partner = VEDHA_PAIRS[bride]
            afflicted = partner is not None and partner == groom
            expected = PoruthamResult.ATHAMAM if afflicted else PoruthamResult.UTHAMAM
            assert result.result is expected, (bride, groom)


def test_vedha_chitra_has_no_partner() -> None:
    assert VEDHA_PAIRS[13] is None
    for other in range(27):
        result = vedha_porutham(make_input(13), make_input(other))
        assert result.result is PoruthamResult.UTHAMAM, other


@pytest.mark.parametrize("bride", range(27))
def test_vedha_pairs_are_mutual(bride: int) -> None:
    partner = VEDHA_PAIRS[bride]
    if partner is not None:
        assert VEDHA_PAIRS[partner] == bride


# ═══════════════════════════════════════════════════════════════════════ #
# Nadi — the traditional eleventh check
# ═══════════════════════════════════════════════════════════════════════ #


@pytest.mark.parametrize("bride", range(27))
def test_nadi_exhaustive(bride: int) -> None:
    for groom in range(27):
        result = nadi_porutham(make_input(bride), make_input(groom))
        same = get_nakshatra_nadi(bride) is get_nakshatra_nadi(groom)
        expected = PoruthamResult.ATHAMAM if same else PoruthamResult.UTHAMAM
        assert result.result is expected, (bride, groom)
        assert result.in_total is False


def test_nadi_not_counted_in_total() -> None:
    result = nadi_porutham(make_input(0), make_input(1))
    assert result.in_total is False
    assert result.result is PoruthamResult.UTHAMAM


# ═══════════════════════════════════════════════════════════════════════ #
# Shared table integrity — every classification row cited in the docs
# ═══════════════════════════════════════════════════════════════════════ #


def test_classification_table_has_27_rows() -> None:
    assert len(NAKSHATRA_CLASSIFICATION) == 27
