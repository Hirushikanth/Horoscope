"""
charts.py — divisional (varga) charts and vargottama detection.

The rasi chart (D1) is subdivided into finer divisional charts. The
Navamsa (D9) is the most important — read for marriage, the spouse and
a graha's true strength — and is drawn beside the D1 in the standard
Tamil layout; D10, D12, D30 and D60 complete the set most Tamil
astrologers routinely consult.

The navamsa-style counting rule (docs/01 §10) applies to D9, D12 and
D60; D10 shifts the dual-sign start to the 7th from itself; D30 uses
the odd/even-sign trimsamsa scheme. All rules below are transcribed
from the reference docs and Brihat Parashara Hora Shastra.

References:
    - docs/01-thirukanitha-jathakam-calculation.md   §10 (navamsa rule,
      varga table, vargottama)
    - Brihat Parashara Hora Shastra, ch. 7 (divisional charts)
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

import numpy as np

from app.vedic.tables import RASI_BY_INDEX, Graha, Rasi

#: Navamsa division span = 3°20′.
NAVAMSA_SPAN_DEG: np.float64 = np.float64(10.0) / np.float64(3.0)
#: Trimsamsa division span = 5°.
TRIMSAMSA_SPAN_DEG: np.float64 = np.float64(5.0)
#: Shashtiamsa division span = 0°30′.
SHASHTIAMSA_SPAN_DEG: np.float64 = np.float64(0.5)


class Varga(StrEnum):
    """The divisional charts supported by the engine."""

    RASI = "D1"
    NAVAMSA = "D9"
    DASAMSA = "D10"
    DWADASAMSA = "D12"
    TRIMSAMSA = "D30"
    SHASHTIAMSA = "D60"


@dataclass(frozen=True)
class VargaPosition:
    """A graha's position in a divisional chart.

    Attributes:
        varga: The divisional chart.
        rasi_index: 0-based sign index of the varga sign (0–11).
        rasi: The varga sign itself.
        division_index: 0-based division within the source sign.
    """

    varga: Varga
    rasi_index: int
    rasi: Rasi
    division_index: int


# ═══════════════════════════════════════════════════════════════════════ #
# Sign natures
# ═══════════════════════════════════════════════════════════════════════ #


def get_sign_nature(rasi_index: int) -> str:
    """Nature of a sign: ``"chara"`` (movable), ``"sthira"`` (fixed) or
    ``"dwisvabhava"`` (dual).

    References:
        docs/01-thirukanitha-jathakam-calculation.md, §10
    """
    if not 0 <= rasi_index <= 11:
        raise ValueError(f"rasi_index must be in 0..11, got {rasi_index}")
    if rasi_index % 3 == 0:
        return "chara"  # Mesha, Karka, Tula, Makara
    if rasi_index % 3 == 1:
        return "sthira"  # Vrishabha, Simha, Vrischika, Kumbha
    return "dwisvabhava"  # Mithuna, Kanya, Dhanus, Meena


def _navamsa_start(rasi_index: int) -> int:
    """Starting sign offset of a navamsa-style count.

    Chara signs count from the sign itself, sthira from the 9th from it,
    dwisvabhava from the 5th from it. Returned as an offset in signs.

    References:
        docs/01-thirukanitha-jathakam-calculation.md, §10
    """
    nature = get_sign_nature(rasi_index)
    if nature == "chara":
        return 0
    if nature == "sthira":
        return 8  # 9th from itself
    return 4  # 5th from itself


# ═══════════════════════════════════════════════════════════════════════ #
# Divisional chart computation
# ═══════════════════════════════════════════════════════════════════════ #


def _varga_division(
    sidereal_longitude: np.float64, division_span: np.float64, divisions: int
) -> tuple[int, int]:
    """Split a longitude into ``(rasi_index, division_index)``."""
    normalized = np.float64(sidereal_longitude) % np.float64(360.0)
    rasi_index = int(normalized // np.float64(30.0))
    within = normalized - np.float64(rasi_index) * np.float64(30.0)
    division_index = min(int(within // division_span), divisions - 1)
    return rasi_index, division_index


def get_navamsa_position(sidereal_longitude: np.float64) -> VargaPosition:
    """Navamsa (D9) sign of a sidereal longitude.

    Each 30° rasi splits into 9 navamsas of 3°20′; which rasi the count
    starts from depends on the sign's nature: chara from the sign
    itself, sthira from the 9th from it, dwisvabhava from the 5th from
    it.

    References:
        docs/01-thirukanitha-jathakam-calculation.md, §10
    """
    rasi_index, division_index = _varga_division(sidereal_longitude, NAVAMSA_SPAN_DEG, 9)
    start = _navamsa_start(rasi_index)
    result = (rasi_index + start + division_index) % 12
    return VargaPosition(Varga.NAVAMSA, result, RASI_BY_INDEX[result], division_index)


def get_dasamsa_position(sidereal_longitude: np.float64) -> VargaPosition:
    """Dasamsa (D10) sign of a sidereal longitude.

    Each sign splits into 10 dasamsas; the count starts from the sign
    itself for chara signs, from the 9th for sthira signs and from the
    7th for dwisvabhava signs.

    References:
        Brihat Parashara Hora Shastra, ch. 7
    """
    rasi_index, division_index = _varga_division(sidereal_longitude, np.float64(3.0), 10)
    nature = get_sign_nature(rasi_index)
    start = 0 if nature == "chara" else (8 if nature == "sthira" else 6)
    result = (rasi_index + start + division_index) % 12
    return VargaPosition(Varga.DASAMSA, result, RASI_BY_INDEX[result], division_index)


def get_dwadasamsa_position(sidereal_longitude: np.float64) -> VargaPosition:
    """Dwadasamsa (D12) sign of a sidereal longitude.

    Twelve dwadasamsas of 2°30′ per sign; the count starts from the
    sign itself (chara), the 9th from it (sthira) or the 5th from it
    (dwisvabhava).

    References:
        Brihat Parashara Hora Shastra, ch. 7
    """
    rasi_index, division_index = _varga_division(sidereal_longitude, np.float64(2.5), 12)
    start = _navamsa_start(rasi_index)
    result = (rasi_index + start + division_index) % 12
    return VargaPosition(Varga.DWADASAMSA, result, RASI_BY_INDEX[result], division_index)


def get_trimsamsa_position(sidereal_longitude: np.float64) -> VargaPosition:
    """Trimsamsa (D30) sign of a sidereal longitude.

    The unequal classical scheme: in **odd** signs the six 5° parts
    count through the odd signs starting from the sign itself; in
    **even** signs they count through the even signs starting from the
    sign itself.

    References:
        Brihat Parashara Hora Shastra, ch. 7 (Trimsamsa)
    """
    rasi_index, division_index = _varga_division(sidereal_longitude, TRIMSAMSA_SPAN_DEG, 6)
    if rasi_index % 2 == 0:  # odd sign (Mesha=0 is the first odd sign)
        sequence = (0, 2, 4, 6, 8, 10)
    else:
        sequence = (1, 3, 5, 7, 9, 11)
    position = sequence.index(rasi_index)
    result = sequence[(position + division_index) % 6]
    return VargaPosition(Varga.TRIMSAMSA, result, RASI_BY_INDEX[result], division_index)


def get_shashtiamsa_position(sidereal_longitude: np.float64) -> VargaPosition:
    """Shashtiamsa (D60) sign of a sidereal longitude.

    Sixty shashtiamsas of 0°30′ per sign; the count starts from the
    sign itself (chara), the 9th from it (sthira) or the 5th from it
    (dwisvabhava) — the same rule as the navamsa.

    References:
        Brihat Parashara Hora Shastra, ch. 7
    """
    rasi_index, division_index = _varga_division(sidereal_longitude, SHASHTIAMSA_SPAN_DEG, 60)
    start = _navamsa_start(rasi_index)
    result = (rasi_index + start + division_index) % 12
    return VargaPosition(Varga.SHASHTIAMSA, result, RASI_BY_INDEX[result], division_index)


def get_varga_position(sidereal_longitude: np.float64, varga: Varga) -> VargaPosition:
    """Sign of a sidereal longitude in the requested divisional chart."""
    if varga is Varga.RASI:
        rasi_index = int(np.float64(sidereal_longitude) % np.float64(360.0) // np.float64(30.0))
        return VargaPosition(Varga.RASI, rasi_index, RASI_BY_INDEX[rasi_index], 0)
    if varga is Varga.NAVAMSA:
        return get_navamsa_position(sidereal_longitude)
    if varga is Varga.DASAMSA:
        return get_dasamsa_position(sidereal_longitude)
    if varga is Varga.DWADASAMSA:
        return get_dwadasamsa_position(sidereal_longitude)
    if varga is Varga.TRIMSAMSA:
        return get_trimsamsa_position(sidereal_longitude)
    return get_shashtiamsa_position(sidereal_longitude)


def is_vargottama(sidereal_longitude: np.float64) -> bool:
    """True when a graha occupies the same sign in D1 and D9.

    A vargottama graha is considered markedly strengthened.

    References:
        docs/01-thirukanitha-jathakam-calculation.md, §10
    """
    rasi_index = int(np.float64(sidereal_longitude) % np.float64(360.0) // np.float64(30.0))
    return get_navamsa_position(sidereal_longitude).rasi_index == rasi_index


def get_graha_vargas(
    positions: dict[Graha, np.float64],
    vargas: tuple[Varga, ...] = (
        Varga.NAVAMSA,
        Varga.DASAMSA,
        Varga.DWADASAMSA,
        Varga.TRIMSAMSA,
        Varga.SHASHTIAMSA,
    ),
) -> dict[Graha, dict[Varga, VargaPosition]]:
    """Divisional-chart signs for every graha.

    Parameters:
        positions: Graha → sidereal longitude (degrees).
        vargas: The divisional charts to compute (D9–D60; D1 is implicit).

    Returns:
        ``{graha: {varga: VargaPosition}}``.
    """
    return {
        graha: {varga: get_varga_position(lon, varga) for varga in vargas}
        for graha, lon in positions.items()
    }
