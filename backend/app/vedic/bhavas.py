"""
bhavas.py — whole-sign houses (Bhava).

In everyday Tamil practice the Rasi chart is read directly as the Bhava
chart: the entire Lagna Rasi is House 1, the next whole Rasi is House 2,
and so on clockwise. Sripati (unequal cusps) is reserved for a later
release — the reference docs explicitly say whole-sign is sufficient for
standard porutham-matching jathakams.

References:
    - docs/01-thirukanitha-jathakam-calculation.md   §8 (Bhava chart)
    - docs/south-indian-horoscope.md                 §2.2 (reading rules)
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from app.vedic.rashi import get_rasi_index, get_rasi_lord
from app.vedic.tables import RASI_BY_INDEX, Graha, Rasi

#: The six kendra (quadrant) house numbers.
KENDRAS: frozenset[int] = frozenset({1, 4, 7, 10})
#: The four trines (trikona) house numbers.
TRIKONAS: frozenset[int] = frozenset({1, 5, 9})
#: The six dusthana house numbers.
DUSTHANAS: frozenset[int] = frozenset({6, 8, 12})


@dataclass(frozen=True)
class Bhava:
    """One whole-sign house.

    Attributes:
        house_number: House number counted clockwise from the lagna (1–12).
        rasi_index: 0-based sign index occupying this house.
        rasi: The sign occupying this house.
        lord: Ruling graha of the house (its sign lord).
    """

    house_number: int
    rasi_index: int
    rasi: Rasi
    lord: Graha


def get_house_number(lagna_rasi_index: int, rasi_index: int) -> int:
    """House number of a sign counted clockwise from the lagna sign.

    The lagna sign itself is House 1; counting proceeds clockwise
    (increasing sign index) and wraps after 12.

    References:
        docs/south-indian-horoscope.md, §2.2
    """
    if not 0 <= lagna_rasi_index <= 11:
        raise ValueError(f"lagna_rasi_index must be in 0..11, got {lagna_rasi_index}")
    if not 0 <= rasi_index <= 11:
        raise ValueError(f"rasi_index must be in 0..11, got {rasi_index}")
    return ((rasi_index - lagna_rasi_index) % 12) + 1


def get_bhava_of_longitude(lagna_rasi_index: int, sidereal_longitude: np.float64) -> int:
    """House number (1–12) of a graha's whole-sign position."""
    return get_house_number(lagna_rasi_index, get_rasi_index(sidereal_longitude))


def get_whole_sign_bhavas(lagna_rasi_index: int) -> list[Bhava]:
    """The 12 whole-sign houses, numbered clockwise from the lagna.

    References:
        docs/01-thirukanitha-jathakam-calculation.md, §8
    """
    if not 0 <= lagna_rasi_index <= 11:
        raise ValueError(f"lagna_rasi_index must be in 0..11, got {lagna_rasi_index}")
    return [
        Bhava(
            house_number=house_number,
            rasi_index=rasi_index,
            rasi=RASI_BY_INDEX[rasi_index],
            lord=get_rasi_lord(rasi_index),
        )
        for house_number, rasi_index in enumerate(
            ((lagna_rasi_index + offset) % 12 for offset in range(12)), start=1
        )
    ]


def house_relations(house_number: int) -> dict[str, bool]:
    """Classical house-group flags for a house number (kendra, trikona, dusthana)."""
    return {
        "kendra": house_number in KENDRAS,
        "trikona": house_number in TRIKONAS,
        "dusthana": house_number in DUSTHANAS,
    }
