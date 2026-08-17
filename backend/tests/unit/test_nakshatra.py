"""Unit tests for nakshatra classification (M2 table-driven cross-checks).

Every row of the reference docs' nakshatra tables is asserted here:

    - docs/02 §2 gana rows (27)
    - docs/02 §5 yoni rows (27, with ♂/♀ gender slots)
    - docs/02 nadi rows (27)
    - docs/02 §9 rajju rows (27, Tamil grouping)
    - docs/02 §10 vedha pairs (13 + Chitra alone)
    - docs/01 §9 pada/lords formulas
"""

from __future__ import annotations

import numpy as np
import pytest
from app.vedic.nakshatra import (
    NAKSHATRA_CLASSIFICATION,
    NAKSHATRA_SPAN_DEG,
    PADA_SPAN_DEG,
    VEDHA_PAIRS,
    Gana,
    Nadi,
    Rajju,
    Yoni,
    get_nakshatra_gana,
    get_nakshatra_index,
    get_nakshatra_lord,
    get_nakshatra_nadi,
    get_nakshatra_pada_index,
    get_nakshatra_rajju,
    get_nakshatra_yoni,
    get_vedha_pair,
    is_vedha_pair,
    yonis_are_enemies,
)

# ═══════════════════════════════════════════════════════════════════════ #
# docs/02 §2 — gana rows
# ═══════════════════════════════════════════════════════════════════════ #

DEVA_NAKSHATRAS = {
    "Ashwini",
    "Mrigashira",
    "Punarvasu",
    "Pushya",
    "Hasta",
    "Swati",
    "Anuradha",
    "Shravana",
    "Revati",
}
MANUSHYA_NAKSHATRAS = {
    "Bharani",
    "Rohini",
    "Ardra",
    "Purva Phalguni",
    "Uttara Phalguni",
    "Purva Ashadha",
    "Uttara Ashadha",
    "Purva Bhadrapada",
    "Uttara Bhadrapada",
}
RAKSHASA_NAKSHATRAS = {
    "Krittika",
    "Ashlesha",
    "Magha",
    "Chitra",
    "Vishakha",
    "Jyeshtha",
    "Mula",
    "Dhanishtha",
    "Shatabhisha",
}

_NAMES = [
    "Ashwini",
    "Bharani",
    "Krittika",
    "Rohini",
    "Mrigashira",
    "Ardra",
    "Punarvasu",
    "Pushya",
    "Ashlesha",
    "Magha",
    "Purva Phalguni",
    "Uttara Phalguni",
    "Hasta",
    "Chitra",
    "Swati",
    "Vishakha",
    "Anuradha",
    "Jyeshtha",
    "Mula",
    "Purva Ashadha",
    "Uttara Ashadha",
    "Shravana",
    "Dhanishtha",
    "Shatabhisha",
    "Purva Bhadrapada",
    "Uttara Bhadrapada",
    "Revati",
]


def _expected_gana(name: str) -> Gana:
    if name in DEVA_NAKSHATRAS:
        return Gana.DEVA
    if name in MANUSHYA_NAKSHATRAS:
        return Gana.MANUSHYA
    return Gana.RAKSHASA


def test_gana_matches_docs_every_row():
    assert len(DEVA_NAKSHATRAS | MANUSHYA_NAKSHATRAS | RAKSHASA_NAKSHATRAS) == 27
    assert DEVA_NAKSHATRAS.isdisjoint(MANUSHYA_NAKSHATRAS)
    for index, name in enumerate(_NAMES):
        assert get_nakshatra_gana(index) == _expected_gana(name), name


# ═══════════════════════════════════════════════════════════════════════ #
# docs/02 §5 — yoni rows (nakshatra, animal, gender)
# ═══════════════════════════════════════════════════════════════════════ #

DOCS_YONI = [
    ("Ashwini", Yoni.HORSE, "male"),
    ("Bharani", Yoni.ELEPHANT, "female"),
    ("Krittika", Yoni.GOAT, "female"),
    ("Rohini", Yoni.SERPENT, "male"),
    ("Mrigashira", Yoni.SERPENT, "female"),
    ("Ardra", Yoni.DOG, "female"),
    ("Punarvasu", Yoni.CAT, "female"),
    ("Pushya", Yoni.GOAT, "male"),
    ("Ashlesha", Yoni.CAT, "male"),
    ("Magha", Yoni.RAT, "male"),
    ("Purva Phalguni", Yoni.RAT, "female"),
    ("Uttara Phalguni", Yoni.COW, "male"),
    ("Hasta", Yoni.BUFFALO, "female"),
    ("Chitra", Yoni.TIGER, "female"),
    ("Swati", Yoni.BUFFALO, "male"),
    ("Vishakha", Yoni.TIGER, "male"),
    ("Anuradha", Yoni.DEER, "female"),
    ("Jyeshtha", Yoni.DEER, "male"),
    ("Mula", Yoni.DOG, "male"),
    ("Purva Ashadha", Yoni.MONKEY, "male"),
    ("Uttara Ashadha", Yoni.MONGOOSE, "male"),
    ("Shravana", Yoni.MONKEY, "female"),
    ("Dhanishtha", Yoni.LION, "female"),
    ("Shatabhisha", Yoni.HORSE, "female"),
    ("Purva Bhadrapada", Yoni.LION, "male"),
    ("Uttara Bhadrapada", Yoni.COW, "female"),
    ("Revati", Yoni.ELEPHANT, "male"),
]


def test_yoni_matches_docs_every_row():
    assert len(DOCS_YONI) == 27
    for index, (name, yoni, gender) in enumerate(DOCS_YONI):
        assignment = get_nakshatra_yoni(index)
        assert assignment.yoni == yoni, name
        assert assignment.gender == gender, name


def test_yoni_enemy_pairs_match_docs():
    """docs/02 §5: Cow↔Tiger, Horse↔Buffalo, Elephant↔Lion, Dog↔Deer,
    Mongoose↔Serpent, Cat↔Rat, Monkey↔Goat."""
    pairs = {
        (Yoni.COW, Yoni.TIGER),
        (Yoni.HORSE, Yoni.BUFFALO),
        (Yoni.ELEPHANT, Yoni.LION),
        (Yoni.DOG, Yoni.DEER),
        (Yoni.MONGOOSE, Yoni.SERPENT),
        (Yoni.CAT, Yoni.RAT),
        (Yoni.MONKEY, Yoni.GOAT),
    }
    assert len(pairs) == 7
    for first, second in pairs:
        assert yonis_are_enemies(first, second)
        assert yonis_are_enemies(second, first)  # mutual
    # non-enemy pairs are not enemies
    assert not yonis_are_enemies(Yoni.COW, Yoni.HORSE)
    assert not yonis_are_enemies(Yoni.HORSE, Yoni.ELEPHANT)
    assert not yonis_are_enemies(Yoni.DOG, Yoni.CAT)


# ═══════════════════════════════════════════════════════════════════════ #
# docs/02 (additional factor) — nadi rows
# ═══════════════════════════════════════════════════════════════════════ #

VATHA_NAKSHATRAS = {
    "Ashwini",
    "Ardra",
    "Punarvasu",
    "Uttara Phalguni",
    "Hasta",
    "Jyeshtha",
    "Mula",
    "Shatabhisha",
    "Purva Bhadrapada",
}
PITHA_NAKSHATRAS = {
    "Bharani",
    "Mrigashira",
    "Pushya",
    "Purva Phalguni",
    "Chitra",
    "Anuradha",
    "Purva Ashadha",
    "Dhanishtha",
    "Uttara Bhadrapada",
}
SLESHMA_NAKSHATRAS = {
    "Krittika",
    "Rohini",
    "Ashlesha",
    "Magha",
    "Swati",
    "Vishakha",
    "Uttara Ashadha",
    "Shravana",
    "Revati",
}


def _expected_nadi(name: str) -> Nadi:
    if name in VATHA_NAKSHATRAS:
        return Nadi.VATHA
    if name in PITHA_NAKSHATRAS:
        return Nadi.PITHA
    return Nadi.SLESHMA


def test_nadi_matches_docs_every_row():
    groups = VATHA_NAKSHATRAS | PITHA_NAKSHATRAS | SLESHMA_NAKSHATRAS
    assert len(groups) == 27
    for index, name in enumerate(_NAMES):
        assert get_nakshatra_nadi(index) == _expected_nadi(name), name


# ═══════════════════════════════════════════════════════════════════════ #
# docs/02 §9 — rajju rows (Tamil grouping)
# ═══════════════════════════════════════════════════════════════════════ #

RAJJU_ROWS = [
    (Rajju.SIRO, {"Chitra", "Mrigashira", "Dhanishtha"}),
    (Rajju.KANTHA, {"Rohini", "Ardra", "Swati", "Hasta", "Shravana", "Shatabhisha"}),
    (
        Rajju.NABHI,
        {
            "Krittika",
            "Punarvasu",
            "Uttara Phalguni",
            "Vishakha",
            "Purva Bhadrapada",
            "Uttara Ashadha",
        },
    ),
    (
        Rajju.KATI,
        {
            "Bharani",
            "Pushya",
            "Purva Phalguni",
            "Anuradha",
            "Uttara Bhadrapada",
            "Purva Ashadha",
        },
    ),
    (Rajju.PADA, {"Ashwini", "Ashlesha", "Magha", "Mula", "Jyeshtha", "Revati"}),
]


def test_rajju_matches_docs_every_row():
    expected: dict[str, Rajju] = {}
    for rajju, names in RAJJU_ROWS:
        for name in names:
            expected[name] = rajju
    assert len(expected) == 27
    for index, name in enumerate(_NAMES):
        assert get_nakshatra_rajju(index) == expected[name], name


# ═══════════════════════════════════════════════════════════════════════ #
# docs/02 §10 — vedha pairs (13 pairs + Chitra without a partner)
# ═══════════════════════════════════════════════════════════════════════ #

DOCS_VEDHA_PAIRS = [
    ("Ashwini", "Jyeshtha"),
    ("Bharani", "Anuradha"),
    ("Krittika", "Vishakha"),
    ("Rohini", "Swati"),
    ("Mrigashira", "Dhanishtha"),
    ("Ardra", "Shravana"),
    ("Punarvasu", "Uttara Ashadha"),
    ("Pushya", "Purva Ashadha"),
    ("Ashlesha", "Mula"),
    ("Magha", "Revati"),
    ("Purva Phalguni", "Uttara Bhadrapada"),
    ("Uttara Phalguni", "Purva Bhadrapada"),
    ("Hasta", "Shatabhisha"),
]


def test_vedha_pairs_match_docs_every_row():
    index_by_name = {name: index for index, name in enumerate(_NAMES)}
    paired = set()
    for first_name, second_name in DOCS_VEDHA_PAIRS:
        first = index_by_name[first_name]
        second = index_by_name[second_name]
        assert get_vedha_pair(first) == second, (first_name, second_name)
        assert get_vedha_pair(second) == first, (second_name, first_name)
        assert is_vedha_pair(first, second)
        assert is_vedha_pair(second, first)  # mutual
        paired.add(first)
        paired.add(second)
    assert len(paired) == 26
    # Chitra (index 13) has no vedha partner
    assert get_vedha_pair(13) is None
    assert not is_vedha_pair(13, 0)
    # same nakshatra is never a vedha pair
    assert not is_vedha_pair(0, 0)
    assert len(VEDHA_PAIRS) == 27
    assert VEDHA_PAIRS.count(None) == 1


# ═══════════════════════════════════════════════════════════════════════ #
# docs/01 §9 — nakshatra spans, padas, lords
# ═══════════════════════════════════════════════════════════════════════ #


def test_spans():
    assert abs(float(NAKSHATRA_SPAN_DEG) - 40.0 / 3.0) < 1e-12  # 13°20′
    assert abs(float(PADA_SPAN_DEG) - 10.0 / 3.0) < 1e-12  # 3°20′
    assert abs(float(NAKSHATRA_SPAN_DEG) * 27.0 - 360.0) < 1e-9


@pytest.mark.parametrize(
    "lon,expected_nakshatra",
    [
        (0.0, 0),  # exactly Ashwini start
        (1e-9, 0),
        (40.0 / 3.0 - 1e-9, 0),
        (40.0 / 3.0, 1),  # Bharani start
        (5.0 * 40.0 / 3.0, 5),  # Ardra
        (13.0 * 40.0 / 3.0, 13),  # Chitra
        (26.0 * 40.0 / 3.0, 26),  # Revati
        (359.999, 26),
    ],
)
def test_nakshatra_index_boundaries(lon, expected_nakshatra):
    assert get_nakshatra_index(np.float64(lon)) == expected_nakshatra


@pytest.mark.parametrize(
    "lon,expected_pada",
    [
        (0.0, 0),
        (10.0 / 3.0 - 1e-9, 0),
        (10.0 / 3.0, 1),
        (20.0 / 3.0, 2),
        (10.0 - 1e-9, 2),  # just before the 4th pada boundary
        (10.0 + 1e-9, 3),  # just after it
        (40.0 / 3.0, 0),  # next nakshatra, pada resets
        (7.0 * 40.0 / 3.0 + 2.0 * 10.0 / 3.0 + 1e-9, 2),
        (7.0 * 40.0 / 3.0 + 10.0 + 1e-9, 3),  # 100° — pada boundary in nakshatra 8
    ],
)
def test_pada_boundaries(lon, expected_pada):
    assert get_nakshatra_pada_index(np.float64(lon)) == expected_pada


def test_108_padas_cover_the_zodiac():
    """27 nakshatras × 4 padas = 108 divisions of 3°20′."""
    for index in range(27):
        for pada in range(4):
            lon = index * NAKSHATRA_SPAN_DEG + pada * PADA_SPAN_DEG + 1e-9
            assert get_nakshatra_index(lon) == index
            assert get_nakshatra_pada_index(lon) == pada


def test_lords_match_docs_sequence():
    expected = ["Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"]
    for index in range(27):
        assert get_nakshatra_lord(index).value == expected[index % 9], index


def test_classification_table_consistency():
    """The internal classification table has exactly 27 rows, one per nakshatra."""
    assert len(NAKSHATRA_CLASSIFICATION) == 27
    for index in range(27):
        gana, yoni, nadi, rajju = NAKSHATRA_CLASSIFICATION[index]
        assert isinstance(gana, Gana)
        assert isinstance(yoni.yoni, Yoni)
        assert yoni.gender in ("male", "female")
        assert isinstance(nadi, Nadi)
        assert isinstance(rajju, Rajju)
