"""
positions.py — geocentric positions of the nine grahas (Navagrahas).

Computes ecliptic longitudes (tropical and sidereal), ecliptic
latitude, geocentric distance, retrogression and solar combustion for:

    Surya (Sun), Chandra (Moon), Chevvai (Mars), Budha (Mercury),
    Guru (Jupiter), Sukra (Venus), Sani (Saturn), Rahu and Ketu.

Rahu/Ketu: classical Thirukanitham practice uses the **mean lunar node**
(a smooth, always-retrograde point, ~18.6-year nodal regression). The
true (osculating) node is available as an option. Mean node is the
default, matching all mainstream South Indian software.

References:
    - docs/01-thirukanitha-jathakam-calculation.md, §4
    - Meeus, "Astronomical Algorithms" (2nd ed.), ch. 47-50
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

import numpy as np
from skyfield.starlib import Star
from skyfield.timelib import Time
from skyfield.vectorlib import VectorSum

from app.astronomy.ayanamsa import get_ayanamsa, tropical_to_sidereal
from app.core.ephemeris_loader import get_earth, get_ephemeris

#: Anything that can be passed to ``Earth.at(t).observe()``:
#: a planetary segment (``VectorSum``) or a fixed star (``Star``).
type GrahaTarget = VectorSum | Star

GRAHA_NAMES = [
    "Sun",
    "Moon",
    "Mars",
    "Mercury",
    "Jupiter",
    "Venus",
    "Saturn",
    "Rahu",
    "Ketu",
]

# Skyfield ephemeris targets for the seven physical grahas.
# DE440 segments are named by barycenter convention; for the inner
# planets barycenter ≡ planet centre (no significant satellites),
# matching the Swiss Ephemeris convention used by astrology software.
_EPH_TARGETS = {
    "Sun": "sun",
    "Moon": "moon",
    "Mars": "mars barycenter",
    "Mercury": "mercury barycenter",
    "Jupiter": "jupiter barycenter",
    "Venus": "venus barycenter",
    "Saturn": "saturn barycenter",
}

# Solar combustion orbs in degrees (Brihat Parashara Hora Shastra).
# Moon is combust within 12°, outer/inner planets within their listed orbs.
COMBUSTION_ORBS: dict[str, float] = {
    "Moon": 12.0,
    "Mars": 17.0,
    "Mercury": 14.0,
    "Jupiter": 11.0,
    "Venus": 10.0,
    "Saturn": 15.0,
}


@dataclass(frozen=True)
class GrahaPosition:
    """Full position state of one graha at a given instant.

    Attributes:
        name: Graha name.
        tropical_longitude: True-of-date ecliptic longitude, degrees.
        sidereal_longitude: Nirayana (Lahiri) longitude, degrees.
        ecliptic_latitude: True-of-date ecliptic latitude, degrees.
        distance_au: Geocentric distance, astronomical units.
        retrograde: True when the graha is in apparent retrograde motion.
        combustion: Dict describing solar combustion state.
    """

    name: str
    tropical_longitude: np.float64
    sidereal_longitude: np.float64
    ecliptic_latitude: np.float64
    distance_au: np.float64
    retrograde: bool
    combustion: dict = field(default_factory=dict)


def _ecliptic_lon_degrees(target: GrahaTarget, t: Time) -> np.float64:
    """Return the true-of-date ecliptic longitude of a target in degrees."""
    earth = get_earth()
    astrometric = earth.at(t).observe(target)
    _, lon, _ = astrometric.ecliptic_latlon(epoch="date")
    return np.float64(lon.degrees)


def _is_retrograde(target: GrahaTarget, t: Time) -> bool:
    """Detect apparent retrograde motion via a float64 derivative.

    Compares ecliptic longitude at ``t ± dt`` (dt = 0.5 day); the sign of
    the angular velocity decides prograde/retrograde. Unwrapping handles
    the 0°/360° boundary.
    """
    dt = np.float64(0.5) / np.float64(24.0)  # half a day, in days
    lon_plus = _ecliptic_lon_degrees(target, t.ts.tai_jd(t.tai + dt))
    lon_minus = _ecliptic_lon_degrees(target, t.ts.tai_jd(t.tai - dt))
    delta = (lon_plus - lon_minus + np.float64(180.0)) % np.float64(360.0) - np.float64(180.0)
    return bool(delta < np.float64(0.0))


def _angular_separation(lon_a: np.float64, lon_b: np.float64) -> np.float64:
    """Shortest angular separation between two longitudes, degrees."""
    delta = np.abs(np.float64(lon_a) - np.float64(lon_b)) % np.float64(360.0)
    return np.float64(np.minimum(delta, np.float64(360.0) - delta))


def _combustion_state(name: str, lon: np.float64, sun_lon: np.float64) -> dict:
    """Compute solar combustion state for a graha.

    References:
        Brihat Parashara Hora Shastra — combustion orbs.
    """
    if name == "Sun":
        return {"combust": False, "separation_deg": None}
    orb = COMBUSTION_ORBS.get(name)
    if orb is None:
        return {"combust": False, "separation_deg": None}
    separation = float(_angular_separation(lon, sun_lon))
    return {
        "combust": separation <= orb,
        "separation_deg": separation,
        "orb_deg": orb,
    }


# ═══════════════════════════════════════════════════════════════════════ #
# Lunar nodes
# ═══════════════════════════════════════════════════════════════════════ #


def get_mean_lunar_node(t: Time) -> np.float64:
    """Mean ascending lunar node longitude (degrees), tropical of date.

    Series from Meeus (2nd ed.) / Swiss Ephemeris definition:
    Ω = 125.0445479 − 1934.1362891·T + 0.0020754·T² + T³/467441 − T⁴/60616000
    with T in Julian centuries from J2000.0 (TT scale).

    References:
        Meeus, "Astronomical Algorithms" (2nd ed.), ch. 50.
    """
    centuries = np.float64((t.tt - 2451545.0) / 36525.0)
    omega = (
        np.float64(125.0445479)
        - np.float64(1934.1362891) * centuries
        + np.float64(0.0020754) * centuries * centuries
        + centuries**3 / np.float64(467441.0)
        - centuries**4 / np.float64(60616000.0)
    )
    return np.float64(omega % np.float64(360.0))


def get_true_lunar_node(t: Time) -> np.float64:
    """Osculating ascending lunar node longitude (degrees), tropical of date.

    Computed from the Moon's geocentric state vector: the ascending node
    direction is the intersection of the Moon's instantaneous orbital
    plane with the ecliptic, n = ẑ × h with h = r × v (ecliptic J2000
    frame), then precessed to the equinox of date.

    References:
        - Vallado, "Fundamentals of Astrodynamics" — osculating elements
        - Meeus, ch. 21 — general precession in longitude
    """
    from skyfield.framelib import ecliptic_frame

    earth = get_earth()
    moon = get_ephemeris()["moon"]
    pos = earth.at(t).observe(moon)  # geocentric state (with velocity)
    rotation = ecliptic_frame.rotation_at(t)
    r_ecl = rotation @ np.asarray(pos.xyz.au, dtype=np.float64)
    v_ecl = rotation @ np.asarray(pos.velocity.km_per_s, dtype=np.float64)

    h = np.cross(r_ecl, v_ecl)  # angular momentum, ecliptic J2000
    n_x = -h[1]
    n_y = h[0]
    omega_j2000 = np.degrees(np.arctan2(n_y, n_x))

    centuries = np.float64((t.tt - 2451545.0) / 36525.0)
    precession = (
        np.float64(5029.0966) * centuries + np.float64(1.11113) * centuries * centuries
    ) / np.float64(3600.0)
    return np.float64((omega_j2000 + precession) % np.float64(360.0))


def get_lunar_node(t: Time, convention: Literal["mean", "true"] = "mean") -> np.float64:
    """Return the lunar node longitude for the requested convention."""
    if convention == "mean":
        return get_mean_lunar_node(t)
    return get_true_lunar_node(t)


# ═══════════════════════════════════════════════════════════════════════ #
# Full position computation
# ═══════════════════════════════════════════════════════════════════════ #


def get_graha_positions(
    t: Time,
    *,
    node_convention: Literal["mean", "true"] = "mean",
) -> dict[str, GrahaPosition]:
    """Compute all nine graha positions at instant ``t``.

    Parameters:
        t: Skyfield time of the birth instant.
        node_convention: ``"mean"`` (classical default) or ``"true"``.

    Returns:
        Dict keyed by graha name (``Sun`` … ``Ketu``) of ``GrahaPosition``.
    """
    earth = get_earth()
    eph = get_ephemeris()
    ayanamsa = get_ayanamsa(t)

    positions: dict[str, GrahaPosition] = {}

    sun_lon = _ecliptic_lon_degrees(eph["sun"], t)

    for name in GRAHA_NAMES:
        if name in ("Rahu", "Ketu"):
            node = np.float64(get_lunar_node(t, node_convention) % np.float64(360.0))
            ketu = np.float64((node + np.float64(180.0)) % np.float64(360.0))
            lon = node if name == "Rahu" else ketu
            positions[name] = GrahaPosition(
                name=name,
                tropical_longitude=lon,
                sidereal_longitude=tropical_to_sidereal(lon, ayanamsa),
                ecliptic_latitude=np.float64(0.0),
                distance_au=np.float64(0.0),
                retrograde=True,  # nodes always move retrograde (mean convention)
                combustion={"combust": False, "separation_deg": None},
            )
            continue

        target = eph[_EPH_TARGETS[name]]
        astrometric = earth.at(t).observe(target)
        ecl_lat, ecl_lon, distance = astrometric.ecliptic_latlon(epoch="date")
        lon = np.float64(ecl_lon.degrees)
        lat = np.float64(ecl_lat.degrees)
        dist = np.float64(distance.au)

        positions[name] = GrahaPosition(
            name=name,
            tropical_longitude=lon,
            sidereal_longitude=tropical_to_sidereal(lon, ayanamsa),
            ecliptic_latitude=lat,
            distance_au=dist,
            retrograde=_is_retrograde(target, t),
            combustion=_combustion_state(name, lon, sun_lon),
        )

    return positions
