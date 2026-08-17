"""
dignity.py — graha dignity: exaltation, debilitation, moolatrikona, own sign.

Classical dignity assessment per Brihat Parashara Hora Shastra: a graha
in its exaltation (Uccham) or debilitation (Neecham) rasi, in its
moolatrikona span, in its own sign (Aatchi — own-sign), or in a neutral
position. The reference docs list the Tamil terms: Uccham, Neecham,
Aatchi.

Notes:
    * Strict classical texts deem a graha *exalted* only at its exact
      exaltation degree; mainstream software treats the exaltation *sign*
      as the exalted position. This module follows the sign-based
      convention and reports the exaltation point and distance so callers
      can apply a stricter orb if desired.
    * Rahu/Ketu have no own signs or moolatrikona; their exaltation
      (Taurus) and debilitation (Scorpio) follow the modern convention.

References:
    - docs/south-indian-horoscope.md   §3.3 (Uccham/Neecham/Aatchi)
    - Brihat Parashara Hora Shastra, ch. 3 (graha strengths)
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

import numpy as np

from app.vedic.rashi import get_rasi_index
from app.vedic.tables import Graha


class Dignity(StrEnum):
    """The dignity statuses, strongest first."""

    EXALTED = "exalted"  # Uccham
    DEBILITATED = "debilitated"  # Neecham
    MOOLATRIKONA = "moolatrikona"
    OWN_SIGN = "own_sign"  # Aatchi
    NEUTRAL = "neutral"


@dataclass(frozen=True)
class ExaltationPoint:
    """Exaltation point of a graha.

    Attributes:
        rasi_index: Sign of exaltation.
        degree_in_sign: Exaltation degree within that sign.
    """

    rasi_index: int
    degree_in_sign: np.float64


#: Exaltation point of each graha — (rasi_index, degree) per BPHS.
EXALTATION_POINTS: dict[Graha, ExaltationPoint] = {
    Graha.SURYA: ExaltationPoint(0, np.float64(10.0)),  # 10° Mesha
    Graha.CHANDRA: ExaltationPoint(1, np.float64(3.0)),  # 3° Vrishabha
    Graha.CHEVVAI: ExaltationPoint(9, np.float64(28.0)),  # 28° Makara
    Graha.BUDHA: ExaltationPoint(5, np.float64(15.0)),  # 15° Kanya
    Graha.GURU: ExaltationPoint(3, np.float64(5.0)),  # 5° Karka
    Graha.SUKRA: ExaltationPoint(11, np.float64(27.0)),  # 27° Meena
    Graha.SANI: ExaltationPoint(6, np.float64(20.0)),  # 20° Tula
    Graha.RAHU: ExaltationPoint(1, np.float64(0.0)),  # Vrishabha (modern)
    Graha.KETU: ExaltationPoint(7, np.float64(0.0)),  # Vrischika (modern)
}

#: Debilitation is always the sign opposite the exaltation sign.
DEBILITATION_POINTS: dict[Graha, ExaltationPoint] = {
    graha: ExaltationPoint(
        rasi_index=(point.rasi_index + 6) % 12,
        degree_in_sign=np.float64(30.0) - point.degree_in_sign,
    )
    for graha, point in EXALTATION_POINTS.items()
}

#: Moolatrikona spans (rasi_index, start_deg, end_deg) per BPHS.
MOOLATRIKONA_SPANS: dict[Graha, tuple[tuple[int, np.float64, np.float64], ...]] = {
    Graha.SURYA: ((4, np.float64(0.0), np.float64(20.0)),),  # Leo 0–20°
    Graha.CHANDRA: ((1, np.float64(3.0), np.float64(30.0)),),  # Taurus 3–30°
    Graha.CHEVVAI: ((0, np.float64(0.0), np.float64(12.0)),),  # Aries 0–12°
    Graha.BUDHA: ((5, np.float64(16.0), np.float64(20.0)),),  # Virgo 16–20°
    Graha.GURU: ((8, np.float64(0.0), np.float64(10.0)),),  # Sagittarius 0–10°
    Graha.SUKRA: ((6, np.float64(0.0), np.float64(15.0)),),  # Libra 0–15°
    Graha.SANI: ((10, np.float64(0.0), np.float64(20.0)),),  # Aquarius 0–20°
    Graha.RAHU: (),
    Graha.KETU: (),
}

#: Own signs of each graha (Rahu/Ketu have none).
OWN_SIGNS: dict[Graha, tuple[int, ...]] = {
    Graha.SURYA: (4,),  # Leo
    Graha.CHANDRA: (3,),  # Cancer
    Graha.CHEVVAI: (0, 7),  # Aries, Scorpio
    Graha.BUDHA: (2, 5),  # Gemini, Virgo
    Graha.GURU: (8, 11),  # Sagittarius, Pisces
    Graha.SUKRA: (1, 6),  # Taurus, Libra
    Graha.SANI: (9, 10),  # Capricorn, Aquarius
    Graha.RAHU: (),
    Graha.KETU: (),
}


@dataclass(frozen=True)
class DignityAssessment:
    """Dignity state of a graha at a longitude.

    Attributes:
        dignity: The strongest dignity that applies.
        rasi_index: Sign occupied by the graha.
        degree_in_sign: Degree within the sign (0–30).
        exaltation_point: The graha's exaltation point (for reference).
        distance_from_exaltation_deg: Angular distance of the graha
            from its exaltation point (within the exaltation sign only).
    """

    dignity: Dignity
    rasi_index: int
    degree_in_sign: np.float64
    exaltation_point: ExaltationPoint
    distance_from_exaltation_deg: np.float64 | None


def get_exaltation_point(graha: Graha) -> ExaltationPoint:
    """Exaltation point of a graha — (sign, degree) per BPHS."""
    try:
        return EXALTATION_POINTS[graha]
    except KeyError:
        raise ValueError(f"unknown graha: {graha}") from None


def get_debilitation_point(graha: Graha) -> ExaltationPoint:
    """Debilitation point — always the sign opposite the exaltation sign."""
    try:
        return DEBILITATION_POINTS[graha]
    except KeyError:
        raise ValueError(f"unknown graha: {graha}") from None


def assess_dignity(graha: Graha, sidereal_longitude: np.float64) -> DignityAssessment:
    """Assess the dignity of a graha at a sidereal longitude.

    The strongest applicable dignity is returned; the exaltation point
    and the degree distance from it (for positions within the
    exaltation sign) are reported for stricter orbs.

    References:
        - Brihat Parashara Hora Shastra, ch. 3
        - docs/south-indian-horoscope.md, §3.3
    """
    if graha not in Graha:
        raise ValueError(f"unknown graha: {graha}")
    normalized = np.float64(sidereal_longitude) % np.float64(360.0)
    rasi_index = get_rasi_index(normalized)
    degree_in_sign = normalized - np.float64(rasi_index) * np.float64(30.0)

    exaltation = get_exaltation_point(graha)
    debilitation = get_debilitation_point(graha)

    dignity = Dignity.NEUTRAL
    distance_from_exaltation: np.float64 | None = None

    if rasi_index == exaltation.rasi_index:
        dignity = Dignity.EXALTED
        distance_from_exaltation = abs(degree_in_sign - exaltation.degree_in_sign)
    elif rasi_index == debilitation.rasi_index:
        dignity = Dignity.DEBILITATED
    else:
        for span_rasi, start, end in MOOLATRIKONA_SPANS.get(graha, ()):
            if rasi_index == span_rasi and start <= degree_in_sign <= end:
                dignity = Dignity.MOOLATRIKONA
                break
        else:
            if rasi_index in OWN_SIGNS[graha]:
                dignity = Dignity.OWN_SIGN

    return DignityAssessment(
        dignity=dignity,
        rasi_index=rasi_index,
        degree_in_sign=degree_in_sign,
        exaltation_point=exaltation,
        distance_from_exaltation_deg=distance_from_exaltation,
    )
