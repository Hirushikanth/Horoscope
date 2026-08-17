"""Unit tests for rashi lordship, vashya groups and Panchadha Maitri.

Cross-checks every row of:

    - docs/01 §9 rasi lords (12 rasis)
    - docs/02 §8 vashya groups (incl. the degree-split halves of
      Dhanus and Makara)
    - docs/02 §7 Panchadha Maitri (all 7 grahas' friend/neutral/enemy
      lists)
"""

from __future__ import annotations

import numpy as np
import pytest
from app.vedic.rashi import (
    MaitriRelation,
    VashyaGroup,
    get_maitri_relation,
    get_mutual_maitri,
    get_rasi_index,
    get_rasi_lord,
    get_vashya_group,
)
from app.vedic.tables import Graha

# ═══════════════════════════════════════════════════════════════════════ #
# docs/01 §9 — rasi lords
# ═══════════════════════════════════════════════════════════════════════ #

DOCS_RASI_LORDS = [
    (Graha.CHEVVAI, "Mars"),  # Mesha
    (Graha.SUKRA, "Venus"),  # Vrishabha
    (Graha.BUDHA, "Mercury"),  # Mithuna
    (Graha.CHANDRA, "Moon"),  # Karka
    (Graha.SURYA, "Sun"),  # Simha
    (Graha.BUDHA, "Mercury"),  # Kanya
    (Graha.SUKRA, "Venus"),  # Tula
    (Graha.CHEVVAI, "Mars"),  # Vrischika
    (Graha.GURU, "Jupiter"),  # Dhanus
    (Graha.SANI, "Saturn"),  # Makara
    (Graha.SANI, "Saturn"),  # Kumbha
    (Graha.GURU, "Jupiter"),  # Meena
]


def test_rasi_lords_match_docs():
    for index, (lord, _) in enumerate(DOCS_RASI_LORDS):
        assert get_rasi_lord(index) == lord, index


@pytest.mark.parametrize(
    "lon,expected",
    [
        (0.0, 0),
        (29.999, 0),
        (30.0, 1),
        (359.999, 11),
    ],
)
def test_rasi_index_boundaries(lon, expected):
    assert get_rasi_index(np.float64(lon)) == expected


# ═══════════════════════════════════════════════════════════════════════ #
# docs/02 §8 — vashya groups
# ═══════════════════════════════════════════════════════════════════════ #

VASHYA_DOCS = [
    # (rasi_index, degree, expected group)
    (0, 14.0, VashyaGroup.CHATUSHPADA),  # Mesham — quadruped
    (0, 29.0, VashyaGroup.CHATUSHPADA),
    (1, 10.0, VashyaGroup.CHATUSHPADA),  # Rishabam — quadruped
    (2, 10.0, VashyaGroup.MANAVA),  # Midhunam — human
    (3, 10.0, VashyaGroup.JALACHARA),  # Kadagam — aquatic
    (4, 10.0, VashyaGroup.VANACHARA),  # Simmam — wild (alone)
    (5, 10.0, VashyaGroup.MANAVA),  # Kanni — human
    (6, 10.0, VashyaGroup.MANAVA),  # Thulaam — human
    (7, 10.0, VashyaGroup.KEETA),  # Vrischikam — insect (alone)
    (8, 14.999, VashyaGroup.MANAVA),  # 1st half of Thanusu — human
    (8, 15.0, VashyaGroup.CHATUSHPADA),  # 2nd half of Thanusu — quadruped
    (9, 14.999, VashyaGroup.CHATUSHPADA),  # 1st half of Makaram — quadruped
    (9, 15.0, VashyaGroup.JALACHARA),  # 2nd half of Makaram — aquatic
    (10, 10.0, VashyaGroup.MANAVA),  # Kumbam — human
    (11, 10.0, VashyaGroup.JALACHARA),  # Meenam — aquatic
]


@pytest.mark.parametrize("rasi_index,degree,expected", VASHYA_DOCS)
def test_vashya_group_matches_docs(rasi_index, degree, expected):
    assert get_vashya_group(rasi_index, np.float64(degree)) == expected


def test_vashya_groups_cover_all_signs():
    for rasi_index in range(12):
        for degree in (0.0, 10.0, 29.0):
            group = get_vashya_group(rasi_index, np.float64(degree))
            assert isinstance(group, VashyaGroup)


# ═══════════════════════════════════════════════════════════════════════ #
# docs/02 §7 — Panchadha Maitri, every cell of the table
# ═══════════════════════════════════════════════════════════════════════ #

DOCS_MAITRI = {
    Graha.SURYA: {
        "friends": {Graha.CHANDRA, Graha.CHEVVAI, Graha.GURU},
        "neutral": {Graha.BUDHA},
        "enemies": {Graha.SUKRA, Graha.SANI},
    },
    Graha.CHANDRA: {
        "friends": {Graha.SURYA, Graha.BUDHA},
        "neutral": {Graha.CHEVVAI, Graha.GURU, Graha.SUKRA, Graha.SANI},
        "enemies": set(),
    },
    Graha.CHEVVAI: {
        "friends": {Graha.SURYA, Graha.CHANDRA, Graha.GURU},
        "neutral": {Graha.SUKRA, Graha.SANI},
        "enemies": {Graha.BUDHA},
    },
    Graha.BUDHA: {
        "friends": {Graha.SURYA, Graha.SUKRA},
        "neutral": {Graha.CHEVVAI, Graha.GURU, Graha.SANI},
        "enemies": {Graha.CHANDRA},
    },
    Graha.GURU: {
        "friends": {Graha.SURYA, Graha.CHANDRA, Graha.CHEVVAI},
        "neutral": {Graha.SANI},
        "enemies": {Graha.BUDHA, Graha.SUKRA},
    },
    Graha.SUKRA: {
        "friends": {Graha.BUDHA, Graha.SANI},
        "neutral": {Graha.CHEVVAI, Graha.GURU},
        "enemies": {Graha.SURYA, Graha.CHANDRA},
    },
    Graha.SANI: {
        "friends": {Graha.BUDHA, Graha.SUKRA},
        "neutral": {Graha.GURU},
        "enemies": {Graha.SURYA, Graha.CHANDRA, Graha.CHEVVAI},
    },
}

PHYSICAL_GRAHAS = (
    Graha.SURYA,
    Graha.CHANDRA,
    Graha.CHEVVAI,
    Graha.BUDHA,
    Graha.GURU,
    Graha.SUKRA,
    Graha.SANI,
)


def test_maitri_matches_docs_every_cell():
    for lord in PHYSICAL_GRAHAS:
        row = DOCS_MAITRI[lord]
        # every other graha is classified exactly once
        all_others = row["friends"] | row["neutral"] | row["enemies"]
        assert all_others == set(PHYSICAL_GRAHAS) - {lord}, lord
        for other in PHYSICAL_GRAHAS:
            if other == lord:
                continue
            if other in row["friends"]:
                assert get_maitri_relation(lord, other) is MaitriRelation.FRIEND
            elif other in row["enemies"]:
                assert get_maitri_relation(lord, other) is MaitriRelation.ENEMY
            else:
                assert get_maitri_relation(lord, other) is MaitriRelation.NEUTRAL


def test_maitri_is_directed():
    """The docs' table is asymmetric (e.g. Budha is Suryan's friend but
    Suryan is Budhan's neutral)."""
    assert get_maitri_relation(Graha.SURYA, Graha.BUDHA) is MaitriRelation.NEUTRAL
    assert get_maitri_relation(Graha.BUDHA, Graha.SURYA) is MaitriRelation.FRIEND


def test_mutual_maitri():
    # Sun & Moon: friends both ways
    assert get_mutual_maitri(Graha.SURYA, Graha.CHANDRA) is MaitriRelation.FRIEND
    # same graha rules both rasis → friends
    assert get_mutual_maitri(Graha.SANI, Graha.SANI) is MaitriRelation.FRIEND
    # Sun & Saturn: enemies both ways
    assert get_mutual_maitri(Graha.SURYA, Graha.SANI) is MaitriRelation.ENEMY
    # Sun & Mercury: one friend, one neutral → neutral
    assert get_mutual_maitri(Graha.SURYA, Graha.BUDHA) is MaitriRelation.NEUTRAL


def test_maitri_rejects_nodes():
    with pytest.raises(ValueError):
        get_maitri_relation(Graha.RAHU, Graha.SURYA)
    with pytest.raises(ValueError):
        get_maitri_relation(Graha.SURYA, Graha.KETU)
    with pytest.raises(ValueError):
        get_mutual_maitri(Graha.RAHU, Graha.KETU)
