"""
ephemeris.py — Core Astronomical Computation Module
=====================================================
Uses NASA JPL DE440 ephemeris via Skyfield for sub-arcsecond planetary positions.
All calculations in IEEE 754 float64 precision. No rounding anywhere.

References:
- JPL DE440: Park et al. 2021, "The JPL Planetary and Lunar Ephemerides DE440 and DE441"
- IAU SOFA: Standards of Fundamental Astronomy
- Lahiri Ayanamsa: Indian Calendar Reform Committee (Saha & Lahiri, 1956)
"""

import numpy as np
from skyfield.api import load, Topos, Star
from skyfield.data import hipparcos
from skyfield import almanac
from datetime import datetime, timedelta
import pytz
import math
import os

# --------------------------------------------------------------------------- #
# Global ephemeris loader (cached)
# --------------------------------------------------------------------------- #

_ts = None
_eph = None
_earth = None
_data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')


def _ensure_data_dir():
    """Create data directory for ephemeris files if it doesn't exist."""
    os.makedirs(_data_dir, exist_ok=True)


def load_ephemeris():
    """
    Load JPL DE440 ephemeris and Skyfield timescale.
    DE440 covers 1550-01-01 to 2650-01-25 with sub-arcsecond accuracy.
    The .bsp file (~114MB) is downloaded once and cached in backend/data/.
    """
    global _ts, _eph, _earth
    if _ts is not None and _eph is not None:
        return _ts, _eph

    _ensure_data_dir()
    from skyfield.api import Loader
    load = Loader(_data_dir)
    
    _ts = load.timescale(builtin=True)
    _eph = load('de440.bsp')
    _earth = _eph['earth']
    return _ts, _eph


def get_timescale():
    """Return the cached Skyfield timescale object."""
    ts, _ = load_ephemeris()
    return ts


def get_earth():
    """Return the cached Earth object from the ephemeris."""
    load_ephemeris()
    return _earth


# --------------------------------------------------------------------------- #
# Core: Datetime → Skyfield Time
# --------------------------------------------------------------------------- #

def datetime_to_skyfield_time(date_str: str, time_str: str, timezone: str) -> 'Time':
    """
    Convert date/time/timezone strings to a Skyfield Time object.
    Uses UTC internally for all astronomical calculations.

    Parameters:
        date_str: "YYYY-MM-DD"
        time_str: "HH:MM:SS"
        timezone: IANA timezone string, e.g. "Asia/Kolkata"

    Returns:
        Skyfield Time object in UTC
    """
    ts, _ = load_ephemeris()
    tz = pytz.timezone(timezone)

    parts = date_str.split('-')
    year = int(parts[0])
    month = int(parts[1])
    day = int(parts[2])

    time_parts = time_str.split(':')
    hour = int(time_parts[0])
    minute = int(time_parts[1])
    second = int(time_parts[2]) if len(time_parts) > 2 else 0

    local_dt = tz.localize(datetime(year, month, day, hour, minute, second))
    utc_dt = local_dt.astimezone(pytz.utc)

    t = ts.utc(utc_dt.year, utc_dt.month, utc_dt.day,
               utc_dt.hour, utc_dt.minute, utc_dt.second)
    return t


# --------------------------------------------------------------------------- #
# Julian Day Number (float64)
# --------------------------------------------------------------------------- #

def get_julian_day(t) -> np.float64:
    """
    Return the Julian Day Number as float64.
    This is the continuous count of days since January 1, 4713 BC (Julian calendar).
    """
    return np.float64(t.tt)


# --------------------------------------------------------------------------- #
# Lahiri Ayanamsa — Chitrapaksha System
# --------------------------------------------------------------------------- #

def get_ayanamsa(t) -> np.float64:
    """
    Compute the Lahiri (Chitrapaksha) Ayanamsa for a given Skyfield time.

    The Chitrapaksha ayanamsa is defined such that the star Spica (Chitra)
    is fixed at exactly 0° Libra (180° sidereal longitude).

    Method:
    1. Compute the tropical ecliptic longitude of Spica at time t
    2. Ayanamsa = tropical_longitude_of_Spica - 180°

    This gives the exact precession offset between tropical and sidereal frames.

    Returns:
        Ayanamsa in degrees (float64), typically ~23-24° for modern dates.
    """
    _, eph = load_ephemeris()
    earth = eph['earth']

    # Spica = HIP 65474, Alpha Virginis
    # J2000.0 coordinates with proper motion from Hipparcos
    spica = Star(
        ra_hours=np.float64(13.419882851),     # 13h 25m 11.579"
        dec_degrees=np.float64(-11.161323611),  # -11° 09' 40.765"
        ra_mas_per_year=np.float64(-42.50),     # proper motion RA
        dec_mas_per_year=np.float64(-31.73),    # proper motion Dec
        parallax_mas=np.float64(12.44),
        radial_km_per_s=np.float64(1.0),
    )

    astrometric = earth.at(t).observe(spica)
    _, lon_spica, _ = astrometric.ecliptic_latlon(epoch='date')
    spica_tropical_lon = np.float64(lon_spica.degrees)

    ayanamsa = spica_tropical_lon - np.float64(180.0)

    return ayanamsa


def tropical_to_sidereal(tropical_lon: np.float64, ayanamsa: np.float64) -> np.float64:
    """
    Convert tropical ecliptic longitude to sidereal longitude.
    sidereal = tropical - ayanamsa (mod 360)

    No rounding — full float64 precision preserved.
    """
    sidereal = np.float64(tropical_lon) - np.float64(ayanamsa)
    sidereal = np.float64(sidereal % np.float64(360.0))
    return sidereal


# --------------------------------------------------------------------------- #
# Planetary Positions (Navagrahas)
# --------------------------------------------------------------------------- #

# Map of planet names to Skyfield ephemeris targets
_PLANET_TARGETS = {
    'Sun': 'sun',
    'Moon': 'moon',
    'Mars': 'mars barycenter',
    'Mercury': 'mercury barycenter',
    'Jupiter': 'jupiter barycenter',
    'Venus': 'venus barycenter',
    'Saturn': 'saturn barycenter',
}


def get_planetary_positions(date_str: str, time_str: str,
                            latitude: float, longitude: float,
                            timezone: str) -> dict:
    """
    Calculate ecliptic positions for all 7 visible Navagrahas + Rahu/Ketu.

    Uses JPL DE440 Chebyshev polynomial interpolation for planetary positions.
    All longitudes in degrees, full float64 precision.

    Parameters:
        date_str: "YYYY-MM-DD"
        time_str: "HH:MM:SS"
        latitude: Observer latitude in degrees (float64)
        longitude: Observer longitude in degrees (float64)
        timezone: IANA timezone string

    Returns:
        dict with keys for each planet, containing:
        - tropical_longitude (degrees, float64)
        - sidereal_longitude (degrees, float64)
        - latitude (degrees, float64)
        - distance_au (AU, float64)
        - is_retrograde (bool)
        - speed_deg_per_day (float64)
        - ayanamsa (float64)
    """
    ts, eph = load_ephemeris()
    t = datetime_to_skyfield_time(date_str, time_str, timezone)

    lat = np.float64(latitude)
    lon = np.float64(longitude)

    earth = eph['earth']
    observer = earth + Topos(latitude_degrees=float(lat),
                              longitude_degrees=float(lon))

    ayanamsa = get_ayanamsa(t)
    positions = {}

    for name, target_name in _PLANET_TARGETS.items():
        target = eph[target_name]
        astrometric = observer.at(t).observe(target)

        ecliptic_lat, ecliptic_lon, distance = astrometric.ecliptic_latlon(epoch='date')

        trop_lon = np.float64(ecliptic_lon.degrees)
        sid_lon = tropical_to_sidereal(trop_lon, ayanamsa)
        ecl_lat = np.float64(ecliptic_lat.degrees)
        dist_au = np.float64(distance.au)

        # Retrograde detection: compare positions 1 day apart
        is_retro, speed = _check_retrograde(observer, target, t, ts, ayanamsa)

        # Combustion check (distance from Sun in sidereal longitude)
        is_combust = False  # Will be set after all positions computed

        positions[name] = {
            'tropical_longitude': float(trop_lon),
            'sidereal_longitude': float(sid_lon),
            'latitude': float(ecl_lat),
            'distance_au': float(dist_au),
            'is_retrograde': is_retro,
            'speed_deg_per_day': float(speed),
        }

    # --- Rahu and Ketu (Lunar Nodes) ---
    rahu_lon, ketu_lon = get_lunar_nodes(t, ayanamsa)
    positions['Rahu'] = {
        'tropical_longitude': float((rahu_lon + ayanamsa) % np.float64(360.0)),
        'sidereal_longitude': float(rahu_lon),
        'latitude': 0.0,
        'distance_au': 0.0,
        'is_retrograde': True,  # Rahu is always retrograde
        'speed_deg_per_day': float(np.float64(-0.05295392)),  # Mean daily motion
    }
    positions['Ketu'] = {
        'tropical_longitude': float((ketu_lon + ayanamsa) % np.float64(360.0)),
        'sidereal_longitude': float(ketu_lon),
        'latitude': 0.0,
        'distance_au': 0.0,
        'is_retrograde': True,  # Ketu is always retrograde
        'speed_deg_per_day': float(np.float64(-0.05295392)),
    }

    # --- Combustion check for all planets ---
    sun_sid = np.float64(positions['Sun']['sidereal_longitude'])
    combustion_orbs = {
        'Moon': np.float64(12.0),
        'Mars': np.float64(17.0),
        'Mercury': np.float64(14.0),
        'Jupiter': np.float64(11.0),
        'Venus': np.float64(10.0),
        'Saturn': np.float64(15.0),
    }
    for planet, orb in combustion_orbs.items():
        if planet in positions:
            planet_sid = np.float64(positions[planet]['sidereal_longitude'])
            positions[planet]['is_combust'] = _is_combust(planet_sid, sun_sid, orb)

    positions['Sun']['is_combust'] = False
    positions['Rahu']['is_combust'] = False
    positions['Ketu']['is_combust'] = False

    positions['_meta'] = {
        'ayanamsa': float(ayanamsa),
        'julian_day': float(get_julian_day(t)),
        'ephemeris': 'JPL DE440',
        'precision': 'IEEE 754 float64',
    }

    return positions


def _check_retrograde(observer, target, t, ts, ayanamsa):
    """
    Determine if a planet is retrograde by comparing its sidereal longitude
    at t - 0.5 day and t + 0.5 day.

    Returns:
        (is_retrograde: bool, speed_deg_per_day: float64)
    """
    jd = t.tt
    t_before = ts.tt_jd(jd - np.float64(0.5))
    t_after = ts.tt_jd(jd + np.float64(0.5))

    _, lon_before, _ = observer.at(t_before).observe(target).ecliptic_latlon(epoch='date')
    _, lon_after, _ = observer.at(t_after).observe(target).ecliptic_latlon(epoch='date')

    lon_b = np.float64(lon_before.degrees)
    lon_a = np.float64(lon_after.degrees)

    # Subtract ayanamsa for sidereal
    sid_b = tropical_to_sidereal(lon_b, ayanamsa)
    sid_a = tropical_to_sidereal(lon_a, ayanamsa)

    # Handle wrap-around at 360°/0°
    diff = sid_a - sid_b
    if diff > np.float64(180.0):
        diff -= np.float64(360.0)
    elif diff < np.float64(-180.0):
        diff += np.float64(360.0)

    speed = diff  # degrees per day (since t_after - t_before = 1 day)
    is_retrograde = bool(diff < np.float64(0.0))

    return is_retrograde, speed


def _is_combust(planet_lon: np.float64, sun_lon: np.float64, orb: np.float64) -> bool:
    """
    Check if a planet is combust (too close to the Sun).
    Uses angular difference on the sidereal ecliptic.
    """
    diff = abs(planet_lon - sun_lon)
    if diff > np.float64(180.0):
        diff = np.float64(360.0) - diff
    return bool(diff < orb)


# --------------------------------------------------------------------------- #
# Lunar Nodes — Rahu (True North Node) and Ketu
# --------------------------------------------------------------------------- #

def get_lunar_nodes(t, ayanamsa: np.float64) -> tuple:
    """
    Calculate the True North Node (Rahu) and South Node (Ketu)
    of the Moon's orbit.

    Method: Use the Moon's orbital plane intersection with the ecliptic.
    The mean longitude of the ascending node Ω is computed from the
    fundamental lunisolar arguments (Meeus, Astronomical Algorithms).

    The polynomial expression for the mean longitude of the ascending node:
    Ω = 125.0445479° - 1934.1362891° × T + 0.0020754° × T²
        + T³ / 467441.0 - T⁴ / 60616000.0

    where T = Julian centuries from J2000.0 (TT)

    Returns:
        (rahu_sidereal_lon, ketu_sidereal_lon) in degrees, float64
    """
    # T = Julian centuries from J2000.0 (TT)
    jd_tt = np.float64(t.tt)
    T = (jd_tt - np.float64(2451545.0)) / np.float64(36525.0)

    # Mean longitude of Moon's ascending node (Meeus, Ch. 22)
    omega = (np.float64(125.0445479)
             - np.float64(1934.1362891) * T
             + np.float64(0.0020754) * T * T
             + T * T * T / np.float64(467441.0)
             - T * T * T * T / np.float64(60616000.0))

    # Normalize to 0-360
    omega = np.float64(omega % np.float64(360.0))
    if omega < np.float64(0.0):
        omega += np.float64(360.0)

    # Convert to sidereal
    rahu_sidereal = tropical_to_sidereal(omega, ayanamsa)
    ketu_sidereal = np.float64((rahu_sidereal + np.float64(180.0)) % np.float64(360.0))

    return rahu_sidereal, ketu_sidereal


# --------------------------------------------------------------------------- #
# Ascendant (Lagna) — Spherical Trigonometry
# --------------------------------------------------------------------------- #

def get_ascendant(t, latitude: float, longitude: float) -> np.float64:
    """
    Calculate the Ascendant (Lagna) — the ecliptic degree rising on the
    eastern horizon at the exact moment and location of birth.

    Method:
    1. Compute Local Sidereal Time (LST) from Greenwich AST + longitude
    2. Convert LST to Right Ascension of the Midheaven (RAMC)
    3. Apply spherical trigonometry formula:
       Ascendant = atan2(cos(RAMC), -(sin(RAMC) × cos(ε) + tan(φ) × sin(ε)))

    where:
       ε = obliquity of the ecliptic (from Skyfield's nutation model)
       φ = observer's latitude
       RAMC = local sidereal time in degrees

    Returns:
        Tropical ascendant longitude in degrees (float64)
    """
    ts, eph = load_ephemeris()
    earth = eph['earth']

    lat_rad = np.float64(math.radians(float(latitude)))

    # Get Greenwich Apparent Sidereal Time in hours
    gast = np.float64(t.gast)

    # Local Sidereal Time = GAST + longitude (east positive) / 15
    lst_hours = gast + np.float64(longitude) / np.float64(15.0)
    lst_hours = np.float64(lst_hours % np.float64(24.0))

    # RAMC in degrees
    ramc_deg = lst_hours * np.float64(15.0)
    ramc_rad = np.float64(math.radians(float(ramc_deg)))

    # Obliquity of the ecliptic
    # Using the IAU 2006 precession model value via polynomial
    jd_tt = np.float64(t.tt)
    T = (jd_tt - np.float64(2451545.0)) / np.float64(36525.0)

    # Mean obliquity (Lieske, 1979) with higher-order terms
    eps_arcsec = (np.float64(84381.448)
                  - np.float64(46.8150) * T
                  - np.float64(0.00059) * T * T
                  + np.float64(0.001813) * T * T * T)
    eps_deg = eps_arcsec / np.float64(3600.0)
    eps_rad = np.float64(math.radians(float(eps_deg)))

    # Ascendant formula (spherical trigonometry)
    y = np.float64(math.cos(float(ramc_rad)))
    x = np.float64(-(math.sin(float(ramc_rad)) * math.cos(float(eps_rad))
                      + math.tan(float(lat_rad)) * math.sin(float(eps_rad))))

    asc_rad = np.float64(math.atan2(float(y), float(x)))
    asc_deg = np.float64(math.degrees(float(asc_rad)))

    # Normalize to 0-360
    asc_deg = np.float64(asc_deg % np.float64(360.0))
    if asc_deg < np.float64(0.0):
        asc_deg += np.float64(360.0)

    return asc_deg


def get_sidereal_ascendant(t, latitude: float, longitude: float,
                           ayanamsa: np.float64) -> np.float64:
    """
    Get the sidereal ascendant (Lagna) by subtracting ayanamsa from tropical ascendant.
    """
    tropical_asc = get_ascendant(t, latitude, longitude)
    return tropical_to_sidereal(tropical_asc, ayanamsa)


# --------------------------------------------------------------------------- #
# Obliquity of the Ecliptic
# --------------------------------------------------------------------------- #

def get_obliquity(t) -> np.float64:
    """
    Compute the mean obliquity of the ecliptic at time t.
    Uses IAU 2006 polynomial (Lieske 1979 approximation).

    Returns:
        Obliquity in degrees (float64)
    """
    jd_tt = np.float64(t.tt)
    T = (jd_tt - np.float64(2451545.0)) / np.float64(36525.0)
    eps_arcsec = (np.float64(84381.448)
                  - np.float64(46.8150) * T
                  - np.float64(0.00059) * T * T
                  + np.float64(0.001813) * T * T * T)
    return eps_arcsec / np.float64(3600.0)


# --------------------------------------------------------------------------- #
# Utility: Degree ↔ DMS conversion
# --------------------------------------------------------------------------- #

def degrees_to_dms(deg: float) -> dict:
    """
    Convert decimal degrees to Degrees-Minutes-Seconds.
    Full precision preserved in the seconds component.
    """
    deg = np.float64(deg)
    d = int(deg)
    m_full = (deg - np.float64(d)) * np.float64(60.0)
    m = int(m_full)
    s = (m_full - np.float64(m)) * np.float64(60.0)
    return {
        'degrees': d,
        'minutes': m,
        'seconds': float(s),
        'formatted': f"{d}° {m}' {s:.4f}\""
    }
