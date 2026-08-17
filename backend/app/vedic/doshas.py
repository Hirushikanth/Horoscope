"""
doshas.py — Chevvai Dosham (Mars affliction) for the individual chart.

Chevvai Dosham (also called Mangal/Kuja Dosha elsewhere in India) arises
when Chevvai (Mars) occupies House 1, 2, 4, 7, 8 or 12 counted from any
of three reference points — the Lagna, the Chandran (Moon) or the
Sukran (Venus). The report records the dosha's presence and from how
many of the three reference points it arises, which is what the Kalyana
Porutham cross-check needs.

Cancellation (parihara) conditions are not evaluated here — the docs
note that a full reading should check them before treating the dosha as
active; that judgement belongs to the reading layer.

References:
    - docs/01-thirukanitha-jathakam-calculation.md   §12 (Chevvai Dosham)
    - docs/02-kalyana-porutham-matching.md           (cross-check)
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from app.vedic.bhavas import get_house_number
from app.vedic.rashi import get_rasi_index

#: The houses that trigger Chevvai Dosham, counted from each reference.
CHEVVAI_DOSHA_HOUSES: frozenset[int] = frozenset({1, 2, 4, 7, 8, 12})


@dataclass(frozen=True)
class ChevvaiDoshamReport:
    """Chevvai Dosham status of one chart.

    Attributes:
        present: True when Mars occupies a dosha house from at least one
            reference point.
        reference_count: Number of reference points (Lagna / Moon /
            Venus) from which the dosha arises (0–3).
        houses_from_lagna: Dosha houses Mars occupies counted from the
            lagna (empty when the dosha does not arise from the lagna).
        houses_from_moon: Same, counted from the Moon.
        houses_from_venus: Same, counted from Venus.
    """

    present: bool
    reference_count: int
    houses_from_lagna: tuple[int, ...]
    houses_from_moon: tuple[int, ...]
    houses_from_venus: tuple[int, ...]


def _dosha_houses_from(mars_rasi_index: int, reference_rasi_index: int) -> tuple[int, ...]:
    """Dosha-house numbers Mars occupies counted from a reference sign."""
    house = get_house_number(reference_rasi_index, mars_rasi_index)
    return (house,) if house in CHEVVAI_DOSHA_HOUSES else ()


def assess_chevvai_dosham(
    mars_sidereal_lon: np.float64,
    lagna_sidereal_lon: np.float64,
    moon_sidereal_lon: np.float64,
    venus_sidereal_lon: np.float64,
) -> ChevvaiDoshamReport:
    """Assess Chevvai Dosham from the three reference points.

    The reference points are the Lagna, the Moon and Venus, counted in
    whole signs (House 1 = the reference sign itself).

    References:
        docs/01-thirukanitha-jathakam-calculation.md, §12
    """
    mars_rasi = get_rasi_index(mars_sidereal_lon)
    from_lagna = _dosha_houses_from(mars_rasi, get_rasi_index(lagna_sidereal_lon))
    from_moon = _dosha_houses_from(mars_rasi, get_rasi_index(moon_sidereal_lon))
    from_venus = _dosha_houses_from(mars_rasi, get_rasi_index(venus_sidereal_lon))

    reference_count = sum(1 for group in (from_lagna, from_moon, from_venus) if group)
    return ChevvaiDoshamReport(
        present=reference_count > 0,
        reference_count=reference_count,
        houses_from_lagna=from_lagna,
        houses_from_moon=from_moon,
        houses_from_venus=from_venus,
    )
