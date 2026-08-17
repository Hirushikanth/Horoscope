"""
nakshatra.py — the 27 lunar mansions and their classical classifications.

Every table here is transcribed from the reference documents and is used
both by the jathakam (birth nakshatra + pada, lord, gana, yoni, nadi,
rajju, vedha) and by the Kalyana Porutham matching engine.

References:
    - docs/01-thirukanitha-jathakam-calculation.md   §9 (spans, padas, lords)
    - docs/02-kalyana-porutham-matching.md           §2 gana, §5 yoni,
      §9 rajju, §10 vedha, and the nadi table
    - docs/south-indian-horoscope.md                 §6.1 (trilingual names)
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

import numpy as np

from app.vedic.tables import Graha

#: One nakshatra = 13°20′ = 360°/27 (float64).
NAKSHATRA_SPAN_DEG: np.float64 = np.float64(360.0) / np.float64(27.0)
#: One pada = 3°20′ = NAKSHATRA_SPAN_DEG / 4.
PADA_SPAN_DEG: np.float64 = NAKSHATRA_SPAN_DEG / np.float64(4.0)


class Gana(StrEnum):
    """The three ganas — docs/02 §2."""

    DEVA = "deva"
    MANUSHYA = "manushya"
    RAKSHASA = "rakshasa"


class Nadi(StrEnum):
    """The three ayurvedic nadis — docs/02 (additional factor)."""

    VATHA = "vatha"
    PITHA = "pitha"
    SLESHMA = "sleshma"


class Rajju(StrEnum):
    """The five rajju body-part groups (Tamil tradition) — docs/02 §9."""

    SIRO = "siro"  # head
    KANTHA = "kantha"  # neck
    NABHI = "nabhi"  # navel/torso
    KATI = "kati"  # waist/thigh
    PADA = "pada"  # feet


class Yoni(StrEnum):
    """The fourteen animal yonis — docs/02 §5."""

    HORSE = "horse"
    ELEPHANT = "elephant"
    GOAT = "goat"
    SERPENT = "serpent"
    DOG = "dog"
    CAT = "cat"
    RAT = "rat"
    COW = "cow"
    BUFFALO = "buffalo"
    TIGER = "tiger"
    DEER = "deer"
    MONKEY = "monkey"
    MONGOOSE = "mongoose"
    LION = "lion"


@dataclass(frozen=True)
class YoniAssignment:
    """The yoni of a nakshatra together with its gender slot.

    The 27 nakshatras fill 27 of the 28 male/female slots of the 14
    yonis; the Mongoose has no opposite-sex pair among the 27.
    """

    yoni: Yoni
    gender: str  # "male" | "female" (docs/02 §5 marks each nakshatra ♂/♀)


# ═══════════════════════════════════════════════════════════════════════ #
# Per-nakshatra classifications — transcribed row-by-row from the docs
# ═══════════════════════════════════════════════════════════════════════ #

#: Nakshatra → (gana, yoni assignment, nadi, rajju).
NAKSHATRA_CLASSIFICATION: tuple[tuple[Gana, YoniAssignment, Nadi, Rajju], ...] = (
    # Ashwini — docs/02 §2 (deva), §5 (Horse ♂), nadi (vatha), §9 (Pada)
    (Gana.DEVA, YoniAssignment(Yoni.HORSE, "male"), Nadi.VATHA, Rajju.PADA),
    # Bharani — manushya, Elephant ♀, pitha, Kati
    (Gana.MANUSHYA, YoniAssignment(Yoni.ELEPHANT, "female"), Nadi.PITHA, Rajju.KATI),
    # Krittika — rakshasa, Goat ♀, sleshma, Nabhi
    (Gana.RAKSHASA, YoniAssignment(Yoni.GOAT, "female"), Nadi.SLESHMA, Rajju.NABHI),
    # Rohini — manushya, Serpent ♂, sleshma, Kantha
    (Gana.MANUSHYA, YoniAssignment(Yoni.SERPENT, "male"), Nadi.SLESHMA, Rajju.KANTHA),
    # Mrigashira — deva, Serpent ♀, pitha, Siro
    (Gana.DEVA, YoniAssignment(Yoni.SERPENT, "female"), Nadi.PITHA, Rajju.SIRO),
    # Ardra — manushya, Dog ♀, vatha, Kantha
    (Gana.MANUSHYA, YoniAssignment(Yoni.DOG, "female"), Nadi.VATHA, Rajju.KANTHA),
    # Punarvasu — deva, Cat ♀, vatha, Nabhi
    (Gana.DEVA, YoniAssignment(Yoni.CAT, "female"), Nadi.VATHA, Rajju.NABHI),
    # Pushya — deva, Goat ♂, pitha, Kati
    (Gana.DEVA, YoniAssignment(Yoni.GOAT, "male"), Nadi.PITHA, Rajju.KATI),
    # Ashlesha — rakshasa, Cat ♂, sleshma, Pada
    (Gana.RAKSHASA, YoniAssignment(Yoni.CAT, "male"), Nadi.SLESHMA, Rajju.PADA),
    # Magha — rakshasa, Rat ♂, sleshma, Pada
    (Gana.RAKSHASA, YoniAssignment(Yoni.RAT, "male"), Nadi.SLESHMA, Rajju.PADA),
    # Purva Phalguni — manushya, Rat ♀, pitha, Kati
    (Gana.MANUSHYA, YoniAssignment(Yoni.RAT, "female"), Nadi.PITHA, Rajju.KATI),
    # Uttara Phalguni — manushya, Cow ♂, vatha, Nabhi
    (Gana.MANUSHYA, YoniAssignment(Yoni.COW, "male"), Nadi.VATHA, Rajju.NABHI),
    # Hasta — deva, Buffalo ♀, vatha, Kantha
    (Gana.DEVA, YoniAssignment(Yoni.BUFFALO, "female"), Nadi.VATHA, Rajju.KANTHA),
    # Chitra — rakshasa, Tiger ♀, pitha, Siro
    (Gana.RAKSHASA, YoniAssignment(Yoni.TIGER, "female"), Nadi.PITHA, Rajju.SIRO),
    # Swati — deva, Buffalo ♂, sleshma, Kantha
    (Gana.DEVA, YoniAssignment(Yoni.BUFFALO, "male"), Nadi.SLESHMA, Rajju.KANTHA),
    # Vishakha — rakshasa, Tiger ♂, sleshma, Nabhi
    (Gana.RAKSHASA, YoniAssignment(Yoni.TIGER, "male"), Nadi.SLESHMA, Rajju.NABHI),
    # Anuradha — deva, Deer ♀, pitha, Kati
    (Gana.DEVA, YoniAssignment(Yoni.DEER, "female"), Nadi.PITHA, Rajju.KATI),
    # Jyeshtha — rakshasa, Deer ♂, vatha, Pada
    (Gana.RAKSHASA, YoniAssignment(Yoni.DEER, "male"), Nadi.VATHA, Rajju.PADA),
    # Mula — rakshasa, Dog ♂, vatha, Pada
    (Gana.RAKSHASA, YoniAssignment(Yoni.DOG, "male"), Nadi.VATHA, Rajju.PADA),
    # Purva Ashadha — manushya, Monkey ♂, pitha, Kati
    (Gana.MANUSHYA, YoniAssignment(Yoni.MONKEY, "male"), Nadi.PITHA, Rajju.KATI),
    # Uttara Ashadha — manushya, Mongoose ♂, sleshma, Nabhi
    (Gana.MANUSHYA, YoniAssignment(Yoni.MONGOOSE, "male"), Nadi.SLESHMA, Rajju.NABHI),
    # Shravana — deva, Monkey ♀, sleshma, Kantha
    (Gana.DEVA, YoniAssignment(Yoni.MONKEY, "female"), Nadi.SLESHMA, Rajju.KANTHA),
    # Dhanishtha — rakshasa, Lion ♀, pitha, Siro
    (Gana.RAKSHASA, YoniAssignment(Yoni.LION, "female"), Nadi.PITHA, Rajju.SIRO),
    # Shatabhisha — rakshasa, Horse ♀, vatha, Kantha
    (Gana.RAKSHASA, YoniAssignment(Yoni.HORSE, "female"), Nadi.VATHA, Rajju.KANTHA),
    # Purva Bhadrapada — manushya, Lion ♂, vatha, Nabhi
    (Gana.MANUSHYA, YoniAssignment(Yoni.LION, "male"), Nadi.VATHA, Rajju.NABHI),
    # Uttara Bhadrapada — manushya, Cow ♀, pitha, Kati
    (Gana.MANUSHYA, YoniAssignment(Yoni.COW, "female"), Nadi.PITHA, Rajju.KATI),
    # Revati — deva, Elephant ♂, sleshma, Pada
    (Gana.DEVA, YoniAssignment(Yoni.ELEPHANT, "male"), Nadi.SLESHMA, Rajju.PADA),
)

#: Nakshatra lords, repeating Ketu → Venus → Sun → Moon → Mars → Rahu →
#: Jupiter → Saturn → Mercury across the 27 (docs/01 §9). Index by
#: ``nakshatra_index``.
NAKSHATRA_LORDS: tuple[Graha, ...] = (
    Graha.KETU,
    Graha.SUKRA,
    Graha.SURYA,
    Graha.CHANDRA,
    Graha.CHEVVAI,
    Graha.RAHU,
    Graha.GURU,
    Graha.SANI,
    Graha.BUDHA,
) * 3

#: Nakshatra → vedha pair (index or ``None``). 13 pairs + Chitra alone.
VEDHA_PAIRS: tuple[int | None, ...] = (
    17,  # Ashwini ↔ Jyeshtha
    16,  # Bharani ↔ Anuradha
    15,  # Krittika ↔ Vishakha
    14,  # Rohini ↔ Swati
    22,  # Mrigashira ↔ Dhanishtha
    21,  # Ardra ↔ Shravana
    20,  # Punarvasu ↔ Uttara Ashadha
    19,  # Pushya ↔ Purva Ashadha
    18,  # Ashlesha ↔ Mula
    26,  # Magha ↔ Revati
    25,  # Purva Phalguni ↔ Uttara Bhadrapada
    24,  # Uttara Phalguni ↔ Purva Bhadrapada
    23,  # Hasta ↔ Shatabhisha
    None,  # Chitra has no vedha partner
    3,  # Rohini ↔ Ashwini
    2,  # Vishakha ↔ Krittika
    1,  # Anuradha ↔ Bharani
    0,  # Jyeshtha ↔ Ashwini
    8,  # Mula ↔ Ashlesha
    7,  # Purva Ashadha ↔ Pushya
    6,  # Uttara Ashadha ↔ Punarvasu
    5,  # Shravana ↔ Ardra
    4,  # Dhanishtha ↔ Mrigashira
    12,  # Shatabhisha ↔ Hasta
    11,  # Purva Bhadrapada ↔ Uttara Phalguni
    10,  # Uttara Bhadrapada ↔ Purva Phalguni
    9,  # Revati ↔ Magha
)

#: Traditional enemy yoni pairs, regardless of gender — docs/02 §5.
YONI_ENEMY_PAIRS: frozenset[frozenset[Yoni]] = frozenset(
    {
        frozenset({Yoni.COW, Yoni.TIGER}),
        frozenset({Yoni.HORSE, Yoni.BUFFALO}),
        frozenset({Yoni.ELEPHANT, Yoni.LION}),
        frozenset({Yoni.DOG, Yoni.DEER}),
        frozenset({Yoni.MONGOOSE, Yoni.SERPENT}),
        frozenset({Yoni.CAT, Yoni.RAT}),
        frozenset({Yoni.MONKEY, Yoni.GOAT}),
    }
)


# ═══════════════════════════════════════════════════════════════════════ #
# Pure positional computations
# ═══════════════════════════════════════════════════════════════════════ #


def get_nakshatra_index(sidereal_longitude: np.float64) -> int:
    """0-based nakshatra index of a sidereal longitude (0–26).

    ``Nakshatra = floor[Moon_long / 13°20′]`` (1-based in the docs; the
    returned index is 0-based for array lookup).

    References:
        docs/01-thirukanitha-jathakam-calculation.md, §5
    """
    normalized = np.float64(sidereal_longitude) % np.float64(360.0)
    return int(normalized // NAKSHATRA_SPAN_DEG)


def get_nakshatra_pada_index(sidereal_longitude: np.float64) -> int:
    """0-based pada index within the nakshatra (0–3).

    ``Pada = floor[(Moon_long mod 13°20′) / 3°20′]`` (1-based in the
    docs; the returned index is 0-based).

    References:
        docs/01-thirukanitha-jathakam-calculation.md, §9
    """
    normalized = np.float64(sidereal_longitude) % np.float64(360.0)
    within = normalized % NAKSHATRA_SPAN_DEG
    return int(within // PADA_SPAN_DEG)


def get_nakshatra_lord(nakshatra_index: int) -> Graha:
    """Ruling graha of the nakshatra (0–26).

    References:
        docs/01-thirukanitha-jathakam-calculation.md, §9
    """
    if not 0 <= nakshatra_index <= 26:
        raise ValueError(f"nakshatra_index must be in 0..26, got {nakshatra_index}")
    return NAKSHATRA_LORDS[nakshatra_index]


def get_nakshatra_gana(nakshatra_index: int) -> Gana:
    """Gana of the nakshatra — docs/02 §2."""
    if not 0 <= nakshatra_index <= 26:
        raise ValueError(f"nakshatra_index must be in 0..26, got {nakshatra_index}")
    return NAKSHATRA_CLASSIFICATION[nakshatra_index][0]


def get_nakshatra_yoni(nakshatra_index: int) -> YoniAssignment:
    """Yoni (and gender slot) of the nakshatra — docs/02 §5."""
    if not 0 <= nakshatra_index <= 26:
        raise ValueError(f"nakshatra_index must be in 0..26, got {nakshatra_index}")
    return NAKSHATRA_CLASSIFICATION[nakshatra_index][1]


def get_nakshatra_nadi(nakshatra_index: int) -> Nadi:
    """Nadi of the nakshatra — docs/02 (additional factor)."""
    if not 0 <= nakshatra_index <= 26:
        raise ValueError(f"nakshatra_index must be in 0..26, got {nakshatra_index}")
    return NAKSHATRA_CLASSIFICATION[nakshatra_index][2]


def get_nakshatra_rajju(nakshatra_index: int) -> Rajju:
    """Rajju (body-part) group of the nakshatra — Tamil grouping, docs/02 §9."""
    if not 0 <= nakshatra_index <= 26:
        raise ValueError(f"nakshatra_index must be in 0..26, got {nakshatra_index}")
    return NAKSHATRA_CLASSIFICATION[nakshatra_index][3]


def get_vedha_pair(nakshatra_index: int) -> int | None:
    """Index of the vedha partner of a nakshatra, or ``None`` (Chitra)."""
    if not 0 <= nakshatra_index <= 26:
        raise ValueError(f"nakshatra_index must be in 0..26, got {nakshatra_index}")
    return VEDHA_PAIRS[nakshatra_index]


def is_vedha_pair(first: int, second: int) -> bool:
    """True when the two nakshatra indices form a vedha (afflicting) pair.

    The pairs are mutual — direction does not matter. ``Chitra`` (13)
    has no partner and never afflicts.

    References:
        docs/02-kalyana-porutham-matching.md, §10
    """
    if first == second:
        return False
    return get_vedha_pair(first) == second or get_vedha_pair(second) == first


def yonis_are_enemies(first: Yoni, second: Yoni) -> bool:
    """True when two yonis form a traditional enemy pair — docs/02 §5.

    The pairs are mutual; gender assignment is irrelevant to the enmity.
    """
    if first == second:
        return False
    return frozenset({first, second}) in YONI_ENEMY_PAIRS
