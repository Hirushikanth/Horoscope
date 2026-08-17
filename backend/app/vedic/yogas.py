"""
yogas.py — classical yogas detectable from the D1 (whole-sign) chart.

The classical corpus is huge; this module implements the yogas most
commonly cited in Tamil practice and computable from sign positions
alone. Every yoga is verified against the classical definition:

    * Pancha Mahapurusha — Ruchaka, Bhadra, Hamsa, Malavya, Sasa
      (graha in its own/exalted sign in a kendra from the lagna)
    * Gajakesari — Jupiter in a kendra from the Moon
    * Budha-Aditya — Sun and Mercury conjunct
    * Chandra-Mangala — Moon and Mars conjunct
    * Sunapha / Anapha / Durudhara — planets in the 2nd/12th from Moon
    * Kemadruma — no planets in the 1st, 2nd or 12th from the Moon
    * Vesi / Vasi / Ubhayachari — planets in the 2nd/12th from the Sun

References:
    - Brihat Parashara Hora Shastra (yoga adhyayas)
    - Saravali (yoga chapter)
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from app.vedic.bhavas import get_house_number
from app.vedic.dignity import Dignity, assess_dignity
from app.vedic.rashi import get_rasi_index
from app.vedic.tables import Graha

#: The seven physical grahas that can form yogas (Rahu/Ketu excluded).
_YOGA_GRAHAS: tuple[Graha, ...] = (
    Graha.SURYA,
    Graha.CHANDRA,
    Graha.CHEVVAI,
    Graha.BUDHA,
    Graha.GURU,
    Graha.SUKRA,
    Graha.SANI,
)


@dataclass(frozen=True)
class YogaResult:
    """A detected yoga.

    Attributes:
        name: Classical name of the yoga.
        present: True when the yoga's conditions hold in this chart.
        detail: Human-readable basis (e.g. the grahas involved).
    """

    name: str
    present: bool
    detail: str = ""


def _in_kendra(lagna_rasi_index: int, rasi_index: int) -> bool:
    return get_house_number(lagna_rasi_index, rasi_index) in (1, 4, 7, 10)


def _sign_of(lon: np.float64) -> int:
    return get_rasi_index(lon)


def _opposite_sign(rasi_index: int) -> int:
    return (rasi_index + 6) % 12


def _conjunct(first: np.float64, second: np.float64) -> bool:
    return _sign_of(first) == _sign_of(second)


def _mahapurusha_yoga(
    graha: Graha,
    name: str,
    positions: dict[Graha, np.float64],
    lagna_rasi_index: int,
) -> YogaResult:
    """A Pancha Mahapurusha yoga: the graha strong (own/exalted) in a kendra."""
    longitude = positions[graha]
    rasi_index = _sign_of(longitude)
    dignity = assess_dignity(graha, longitude).dignity
    present = dignity in (Dignity.EXALTED, Dignity.MOOLATRIKONA, Dignity.OWN_SIGN) and _in_kendra(
        lagna_rasi_index, rasi_index
    )
    return YogaResult(
        name=name,
        present=present,
        detail=(
            f"{graha.value} in sign {rasi_index + 1}, dignity {dignity.value}"
            f", kendra from lagna: {_in_kendra(lagna_rasi_index, rasi_index)}"
        ),
    )


def _planets_in_house_from(
    house_number: int, reference_rasi: int, positions: dict[Graha, np.float64]
) -> list[Graha]:
    """Grahas (excluding Sun/Moon/Rahu/Ketu) in a house from a reference sign."""
    found: list[Graha] = []
    for graha in positions:
        if graha in (Graha.SURYA, Graha.CHANDRA, Graha.RAHU, Graha.KETU):
            continue
        if get_house_number(reference_rasi, _sign_of(positions[graha])) == house_number:
            found.append(graha)
    return found


def detect_yogas(
    lagna_rasi_index: int,
    positions: dict[Graha, np.float64],
) -> list[YogaResult]:
    """Detect the classical yogas in a D1 chart.

    Parameters:
        lagna_rasi_index: 0-based sign index of the lagna.
        positions: Graha → sidereal longitude (degrees) for the chart.

    Returns:
        A ``YogaResult`` for every supported yoga, whether present or not
        (so callers can render a complete "yogas considered" list).
    """
    moon_rasi = _sign_of(positions[Graha.CHANDRA])
    sun_rasi = _sign_of(positions[Graha.SURYA])

    results: list[YogaResult] = [
        _mahapurusha_yoga(Graha.CHEVVAI, "Ruchaka", positions, lagna_rasi_index),
        _mahapurusha_yoga(Graha.BUDHA, "Bhadra", positions, lagna_rasi_index),
        _mahapurusha_yoga(Graha.GURU, "Hamsa", positions, lagna_rasi_index),
        _mahapurusha_yoga(Graha.SUKRA, "Malavya", positions, lagna_rasi_index),
        _mahapurusha_yoga(Graha.SANI, "Sasa", positions, lagna_rasi_index),
    ]

    # Gajakesari — Jupiter in a kendra from the Moon.
    jupiter_rasi = _sign_of(positions[Graha.GURU])
    gajakesari = get_house_number(moon_rasi, jupiter_rasi) in (1, 4, 7, 10)
    results.append(
        YogaResult(
            name="Gajakesari",
            present=gajakesari,
            detail=f"Jupiter in house {get_house_number(moon_rasi, jupiter_rasi)} from Moon",
        )
    )

    # Budha-Aditya — Sun and Mercury conjunct.
    results.append(
        YogaResult(
            name="Budha-Aditya",
            present=_conjunct(positions[Graha.SURYA], positions[Graha.BUDHA]),
            detail="Sun and Mercury in the same sign",
        )
    )

    # Chandra-Mangala — Moon and Mars conjunct.
    results.append(
        YogaResult(
            name="Chandra-Mangala",
            present=_conjunct(positions[Graha.CHANDRA], positions[Graha.CHEVVAI]),
            detail="Moon and Mars in the same sign",
        )
    )

    # Sunapha/Anapha/Durudhara — planets in the 2nd/12th from the Moon.
    second_from_moon = _planets_in_house_from(2, moon_rasi, positions)
    twelfth_from_moon = _planets_in_house_from(12, moon_rasi, positions)
    sunapha = bool(second_from_moon)
    anapha = bool(twelfth_from_moon)
    results.append(
        YogaResult(
            name="Sunapha",
            present=sunapha,
            detail=f"planets in 2nd from Moon: {[g.value for g in second_from_moon]}",
        )
    )
    results.append(
        YogaResult(
            name="Anapha",
            present=anapha,
            detail=f"planets in 12th from Moon: {[g.value for g in twelfth_from_moon]}",
        )
    )
    results.append(
        YogaResult(
            name="Durudhara",
            present=sunapha and anapha,
            detail="planets in both the 2nd and 12th from Moon",
        )
    )

    # Kemadruma — no planets (other than the Moon) in houses 1, 2, 12 from the Moon.
    kemadruma_planets = [
        graha
        for graha in _YOGA_GRAHAS
        if graha is not Graha.CHANDRA
        and get_house_number(moon_rasi, _sign_of(positions[graha])) in (1, 2, 12)
    ]
    results.append(
        YogaResult(
            name="Kemadruma",
            present=not kemadruma_planets,
            detail=(f"houses 1/2/12 from Moon occupied: {[g.value for g in kemadruma_planets]}"),
        )
    )

    # Vesi/Vasi/Ubhayachari — planets in the 2nd/12th from the Sun.
    second_from_sun = _planets_in_house_from(2, sun_rasi, positions)
    twelfth_from_sun = _planets_in_house_from(12, sun_rasi, positions)
    vesi = bool(second_from_sun)
    vasi = bool(twelfth_from_sun)
    results.append(
        YogaResult(
            name="Vesi",
            present=vesi,
            detail=f"planets in 2nd from Sun: {[g.value for g in second_from_sun]}",
        )
    )
    results.append(
        YogaResult(
            name="Vasi",
            present=vasi,
            detail=f"planets in 12th from Sun: {[g.value for g in twelfth_from_sun]}",
        )
    )
    results.append(
        YogaResult(
            name="Ubhayachari",
            present=vesi and vasi,
            detail="planets in both the 2nd and 12th from Sun",
        )
    )

    return results
