"""
ascendant.py — the Lagna (Ascendant).

The Lagna is the sidereal ecliptic degree rising on the eastern horizon
at the exact birth instant and place — the most time-sensitive point of
the chart (≈1° every 4 minutes, one sign every ~2 hours).

Computation steps (all float64):
    1. GMST = 280.46061837 + 360.98564736629·(JD − 2451545.0)
              + 0.000387933·T² − T³/38710000,  T = (JD − 2451545.0)/36525
    2. LST = GMST + longitude_east
    3. Tropical ascendant:
         λ = atan2( cos(LST), −( sin(LST)·cos(ε) + tan(φ)·sin(ε) ) )
    4. Sidereal lagna = Tropical − Ayanamsa

NOTE on sign convention: the formula above places the *rising* (eastern
horizon) point. With the opposite sign the same expression returns the
descendant. The reference document (docs §6) writes the numerator terms
with a different sign; the formula implemented here is verified against
the horizon condition in tests, which is what accuracy demands.

References:
    - Meeus, "Astronomical Algorithms" (2nd ed.), ch. 12 (sidereal time)
    - docs/01-thirukanitha-jathakam-calculation.md, §6
"""

from __future__ import annotations

import numpy as np
from skyfield.timelib import Time

from app.astronomy.ayanamsa import tropical_to_sidereal

# ═══════════════════════════════════════════════════════════════════════ #
# Sidereal time and obliquity
# ═══════════════════════════════════════════════════════════════════════ #


def get_obliquity(t: Time) -> np.float64:
    """Mean obliquity of the ecliptic (degrees) at instant ``t``.

    IAU 1976 / Meeus series:
    ε = 23.43929111 − 0.013004167·T − 1.6389e-7·T² + 5.0361e-7·T³

    References:
        Meeus, "Astronomical Algorithms" (2nd ed.), ch. 22.
    """
    centuries = np.float64((t.tt - 2451545.0) / 36525.0)
    epsilon = (
        np.float64(23.43929111)
        - np.float64(0.013004167) * centuries
        - np.float64(1.6389e-7) * centuries * centuries
        + np.float64(5.0361e-7) * centuries**3
    )
    return np.float64(epsilon)


def get_gmst_degrees(t: Time) -> np.float64:
    """Greenwich Mean Sidereal Time in degrees at instant ``t`` (UT1 scale).

    Formula per the reference document (Meeus-based), using the UT1
    Julian day.

    References:
        docs/01-thirukanitha-jathakam-calculation.md, §6
    """
    jd_ut = np.float64(t.ut1)
    centuries = np.float64((jd_ut - 2451545.0) / 36525.0)
    gmst = (
        np.float64(280.46061837)
        + np.float64(360.98564736629) * (jd_ut - np.float64(2451545.0))
        + np.float64(0.000387933) * centuries * centuries
        - centuries**3 / np.float64(38710000.0)
    )
    return np.float64(gmst % np.float64(360.0))


# ═══════════════════════════════════════════════════════════════════════ #
# Ascendant
# ═══════════════════════════════════════════════════════════════════════ #


def get_ascendant(t: Time, latitude: float, longitude: float) -> np.float64:
    """Tropical ascendant longitude (degrees) at the birth instant.

    Parameters:
        t: Skyfield time of birth.
        latitude: Geographic latitude, degrees (north positive).
        longitude: Geographic longitude, degrees (east positive).

    Returns:
        Tropical ecliptic longitude of the rising point, [0, 360).
    """
    gmst = get_gmst_degrees(t)
    lst = np.float64(gmst + np.float64(longitude))
    lst_rad = np.radians(lst)

    phi = np.radians(np.float64(latitude))
    epsilon_rad = np.radians(get_obliquity(t))

    # λ = atan2( cos(LST), −( sin(LST)·cos(ε) + tan(φ)·sin(ε) ) )
    numerator = np.cos(lst_rad)
    denominator = -(np.sin(lst_rad) * np.cos(epsilon_rad) + np.tan(phi) * np.sin(epsilon_rad))

    asc = np.degrees(np.arctan2(numerator, denominator))
    return np.float64(asc % np.float64(360.0))


def get_sidereal_ascendant(
    t: Time,
    latitude: float,
    longitude: float,
    ayanamsa: np.float64,
) -> np.float64:
    """Sidereal (nirayana) Lagna longitude at the birth instant.

    Parameters:
        t: Skyfield time of birth.
        latitude: Geographic latitude, degrees.
        longitude: Geographic longitude, degrees.
        ayanamsa: Lahiri ayanamsa at ``t``, degrees.

    Returns:
        Sidereal longitude of the Lagna, [0, 360).
    """
    asc_tropical = get_ascendant(t, latitude, longitude)
    return tropical_to_sidereal(asc_tropical, ayanamsa)
