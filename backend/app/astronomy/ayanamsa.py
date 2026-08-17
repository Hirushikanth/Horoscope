"""
ayanamsa.py — the sidereal zodiac correction (Ayanamsa).

Jathakam is cast on the sidereal (nirayana) zodiac, fixed against the
stars; the tropical zodiac drifts against the stars by ≈50.29″/year due
to precession of the equinoxes. The offset is the Ayanamsa.

Thirukanitham practice uses the **Lahiri (Chitrapaksha)** ayanamsa: the
star Chitra (Spica, α Virginis, HIP 65474) is fixed at exactly 0° Libra
(180°) in the sidereal zodiac — the definition adopted by the Government
of India's Calendar Reform Committee (1955) for the Rashtriya Panchang.

References:
    - docs/01-thirukanitha-jathakam-calculation.md, §3
    - Saha & Lahiri (1956), "History of the Calendar"
    - Park et al. 2021 (DE440) — Spica positions via JPL ephemeris
"""

from __future__ import annotations

from enum import StrEnum

import numpy as np
from skyfield.api import Star
from skyfield.timelib import Time

from app.core.ephemeris_loader import get_earth

# ═══════════════════════════════════════════════════════════════════════ #
# Ayanamsa systems
# ═══════════════════════════════════════════════════════════════════════ #


class AyanamsaSystem(StrEnum):
    """Supported ayanamsa systems.

    Only ``LAHIRI`` is implemented (the Thirukanitham standard).
    Others are reserved for future releases.
    """

    LAHIRI = "lahiri"
    RAMAN = "raman"
    KP = "kp"


# ═══════════════════════════════════════════════════════════════════════ #
# Chitra (Spica) — the anchor of the Chitrapaksha system
# ═══════════════════════════════════════════════════════════════════════ #
# ICRS J2000 coordinates and proper motion from the Hipparcos catalogue
# (HIP 65474), used with light-time-independent astrometric reduction so
# that Sidereal(Spica) ≡ 180° by construction.

SPICA = Star(
    ra_hours=np.float64(13.4198830833),  # 13h 25m 11.579s
    dec_degrees=np.float64(-11.1613194444),  # -11° 09' 40.75"
    ra_mas_per_year=np.float64(-42.50),
    dec_mas_per_year=np.float64(-31.73),
    parallax_mas=np.float64(12.44),
)


def get_lahiri_ayanamsa(t: Time) -> np.float64:
    """Return the Lahiri (Chitrapaksha) ayanamsa in degrees for instant ``t``.

    Definition: the tropical ecliptic longitude of Chitra (Spica) minus
    exactly 180° (Spica is fixed at 0° Libra in the sidereal zodiac).
    Precession and proper motion are handled by the DE440-based
    astrometric reduction.

    Returns:
        Ayanamsa in degrees, in [0, 360), as ``np.float64``.
    """
    earth = get_earth()
    astrometric = earth.at(t).observe(SPICA)
    _, ecl_lon, _ = astrometric.ecliptic_latlon(epoch="date")
    ayanamsa = np.float64(ecl_lon.degrees) - np.float64(180.0)
    return np.float64(ayanamsa % np.float64(360.0))


def get_ayanamsa(t: Time, system: AyanamsaSystem = AyanamsaSystem.LAHIRI) -> np.float64:
    """Return the ayanamsa for the requested system (Lahiri default).

    Raises:
        UnsupportedFeatureError: for systems not yet implemented.
    """
    from app.exceptions import UnsupportedFeatureError

    if system is AyanamsaSystem.LAHIRI:
        return get_lahiri_ayanamsa(t)
    raise UnsupportedFeatureError(
        f"Ayanamsa system '{system.value}' is reserved but not implemented.",
        context={"system": system.value},
    )


def tropical_to_sidereal(tropical_lon: np.float64, ayanamsa: np.float64) -> np.float64:
    """Convert a tropical longitude to sidereal (nirayana) longitude.

    ``Sidereal = Tropical − Ayanamsa``, normalised to [0, 360).

    References:
        docs/01-thirukanitha-jathakam-calculation.md, §3
    """
    sidereal = np.float64(tropical_lon) - np.float64(ayanamsa)
    return np.float64(sidereal % np.float64(360.0))
