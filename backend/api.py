"""
api.py — REST API Endpoints for Jyotisha
==========================================
8 POST endpoints serving complete Vedic astrology data.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
import numpy as np
from datetime import datetime
import pytz

from ephemeris import (
    load_ephemeris, datetime_to_skyfield_time, get_planetary_positions,
    get_ayanamsa, get_sidereal_ascendant, degrees_to_dms, get_julian_day,
)
from vedic import (
    get_nakshatra, get_rashi, get_bhava, get_janma_nakshatra,
    get_vimshottari_dasha, get_panchang, get_divisional_charts,
    detect_yogas, get_planetary_dignity,
)
from matching import compute_kundali_matching
from stars import get_star_positions

router = APIRouter()


def sanitize_numpy(obj):
    """Recursively convert numpy types to native Python types for JSON serialization."""
    if isinstance(obj, dict):
        return {k: sanitize_numpy(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [sanitize_numpy(v) for v in obj]
    elif isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.bool_):
        return bool(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    return obj



class BirthData(BaseModel):
    date: str = Field(..., example="1990-01-15", description="Birth date YYYY-MM-DD")
    time: str = Field(..., example="06:00:00", description="Birth time HH:MM:SS")
    latitude: float = Field(..., example=13.0827, description="Latitude in degrees")
    longitude: float = Field(..., example=80.2707, description="Longitude in degrees")
    timezone: str = Field(..., example="Asia/Kolkata", description="IANA timezone")


def _get_weekday(date_str: str, time_str: str, timezone: str) -> int:
    """Return weekday (0=Mon .. 6=Sun) for the given local date/time."""
    tz = pytz.timezone(timezone)
    parts = date_str.split('-')
    tparts = time_str.split(':')
    dt = tz.localize(datetime(int(parts[0]), int(parts[1]), int(parts[2]),
                              int(tparts[0]), int(tparts[1]),
                              int(tparts[2]) if len(tparts) > 2 else 0))
    # Convert Python weekday (Mon=0) to Jyotisha convention (Sun=0)
    py_weekday = dt.weekday()
    return (py_weekday + 1) % 7  # Mon=1,Tue=2,...,Sun=0


# ═══════════════════════════════════════════════════════════════════════════ #
# 1. FULL HOROSCOPE
# ═══════════════════════════════════════════════════════════════════════════ #

@router.post("/horoscope")
async def compute_horoscope(data: BirthData):
    """Complete horoscope: planets, houses, nakshatra, dasha, panchang, yogas, charts."""
    try:
        ts, eph = load_ephemeris()
        t = datetime_to_skyfield_time(data.date, data.time, data.timezone)

        # Planetary positions
        positions = get_planetary_positions(data.date, data.time, data.latitude,
                                            data.longitude, data.timezone)
        ayanamsa = np.float64(positions['_meta']['ayanamsa'])

        # Sidereal Ascendant (Lagna)
        asc_sid = get_sidereal_ascendant(t, data.latitude, data.longitude, ayanamsa)
        asc_rashi = get_rashi(float(asc_sid))
        asc_nak = get_nakshatra(float(asc_sid))

        # Add nakshatra, rashi, dignity to each planet
        for name, pdata in positions.items():
            if name.startswith('_'):
                continue
            sid = pdata['sidereal_longitude']
            pdata['nakshatra'] = get_nakshatra(sid)
            pdata['rashi'] = get_rashi(sid)
            pdata['dms'] = degrees_to_dms(sid)
            pdata['dignity'] = get_planetary_dignity(name, sid)

        # Bhavas (Houses)
        bhavas = get_bhava(positions, float(asc_sid))

        # Janma Nakshatra
        moon_sid = positions['Moon']['sidereal_longitude']
        janma = get_janma_nakshatra(moon_sid)

        # Weekday for panchang
        weekday = _get_weekday(data.date, data.time, data.timezone)
        sun_sid = positions['Sun']['sidereal_longitude']
        panchang = get_panchang(sun_sid, moon_sid, weekday)

        # Vimshottari Dasha
        dasha = get_vimshottari_dasha(moon_sid, data.date)

        # Divisional charts
        charts = get_divisional_charts(positions)

        # Yogas
        yogas = detect_yogas(positions, bhavas)

        return sanitize_numpy({
            'ascendant': {
                'sidereal_longitude': float(asc_sid),
                'dms': degrees_to_dms(float(asc_sid)),
                'rashi': asc_rashi,
                'nakshatra': asc_nak,
            },
            'planets': positions,
            'bhavas': bhavas,
            'janma_nakshatra': janma,
            'panchang': panchang,
            'dasha': dasha,
            'divisional_charts': charts,
            'yogas': yogas,
            'birth_data': {
                'date': data.date,
                'time': data.time,
                'latitude': data.latitude,
                'longitude': data.longitude,
                'timezone': data.timezone,
            },
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ═══════════════════════════════════════════════════════════════════════════ #
# 2. PLANETS ONLY
# ═══════════════════════════════════════════════════════════════════════════ #

@router.post("/planets")
async def compute_planets(data: BirthData):
    """Planetary positions only with nakshatra, rashi, and dignity."""
    try:
        positions = get_planetary_positions(data.date, data.time, data.latitude,
                                            data.longitude, data.timezone)
        for name, pdata in positions.items():
            if name.startswith('_'):
                continue
            sid = pdata['sidereal_longitude']
            pdata['nakshatra'] = get_nakshatra(sid)
            pdata['rashi'] = get_rashi(sid)
            pdata['dms'] = degrees_to_dms(sid)
            pdata['dignity'] = get_planetary_dignity(name, sid)
        return sanitize_numpy(positions)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ═══════════════════════════════════════════════════════════════════════════ #
# 3. DASHA TIMELINE
# ═══════════════════════════════════════════════════════════════════════════ #

@router.post("/dasha")
async def compute_dasha(data: BirthData):
    """Vimshottari Dasha timeline."""
    try:
        positions = get_planetary_positions(data.date, data.time, data.latitude,
                                            data.longitude, data.timezone)
        moon_sid = positions['Moon']['sidereal_longitude']
        return sanitize_numpy(get_vimshottari_dasha(moon_sid, data.date))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ═══════════════════════════════════════════════════════════════════════════ #
# 4. PANCHANG
# ═══════════════════════════════════════════════════════════════════════════ #

@router.post("/panchang")
async def compute_panchang(data: BirthData):
    """Panchang: Tithi, Vara, Nakshatra, Yoga, Karana."""
    try:
        positions = get_planetary_positions(data.date, data.time, data.latitude,
                                            data.longitude, data.timezone)
        weekday = _get_weekday(data.date, data.time, data.timezone)
        sun_sid = positions['Sun']['sidereal_longitude']
        moon_sid = positions['Moon']['sidereal_longitude']
        return sanitize_numpy(get_panchang(sun_sid, moon_sid, weekday))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ═══════════════════════════════════════════════════════════════════════════ #
# 5. FIXED STARS
# ═══════════════════════════════════════════════════════════════════════════ #

@router.post("/stars")
async def compute_stars(data: BirthData):
    """Fixed star positions at the birth moment."""
    try:
        ts, eph = load_ephemeris()
        t = datetime_to_skyfield_time(data.date, data.time, data.timezone)
        ayanamsa = float(get_ayanamsa(t))
        from skyfield.api import Topos
        earth = eph['earth']
        observer = earth + Topos(latitude_degrees=data.latitude,
                                  longitude_degrees=data.longitude)
        stars = get_star_positions(t, ayanamsa, observer)
        return sanitize_numpy({'ayanamsa': ayanamsa, 'stars': stars, 'count': len(stars)})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ═══════════════════════════════════════════════════════════════════════════ #
# 6. DIVISIONAL CHARTS
# ═══════════════════════════════════════════════════════════════════════════ #

@router.post("/divisional")
async def compute_divisional(data: BirthData):
    """Divisional charts: D-1 (Rasi), D-9 (Navamsa), D-10 (Dasamsa)."""
    try:
        positions = get_planetary_positions(data.date, data.time, data.latitude,
                                            data.longitude, data.timezone)
        return sanitize_numpy(get_divisional_charts(positions))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ═══════════════════════════════════════════════════════════════════════════ #
# 7. BHAVAS (HOUSES)
# ═══════════════════════════════════════════════════════════════════════════ #

@router.post("/bhavas")
async def compute_bhavas(data: BirthData):
    """12 Bhavas (Houses) with lords, occupants, and significations."""
    try:
        ts, eph = load_ephemeris()
        t = datetime_to_skyfield_time(data.date, data.time, data.timezone)
        positions = get_planetary_positions(data.date, data.time, data.latitude,
                                            data.longitude, data.timezone)
        ayanamsa = np.float64(positions['_meta']['ayanamsa'])
        asc_sid = get_sidereal_ascendant(t, data.latitude, data.longitude, ayanamsa)
        return sanitize_numpy(get_bhava(positions, float(asc_sid)))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ═══════════════════════════════════════════════════════════════════════════ #
# 8. KUNDALI MATCHING — Ashta Koota Milan
# ═══════════════════════════════════════════════════════════════════════════ #

class MatchingData(BaseModel):
    """Input model for Kundali Matching — accepts birth data for two individuals."""
    bride: BirthData = Field(..., description="Bride's birth data")
    groom: BirthData = Field(..., description="Groom's birth data")
    system: str = Field(
        default="both",
        description="Matching system to use: 'north_indian', 'south_indian', or 'both'."
    )


def _compute_person(data: BirthData) -> tuple[dict, float]:
    """
    Compute planetary positions and sidereal ascendant for one person.
    Returns (planets dict, sidereal ascendant longitude).
    """
    ts, eph = load_ephemeris()
    t = datetime_to_skyfield_time(data.date, data.time, data.timezone)
    positions = get_planetary_positions(
        data.date, data.time, data.latitude, data.longitude, data.timezone
    )
    ayanamsa = np.float64(positions['_meta']['ayanamsa'])
    asc_sid = get_sidereal_ascendant(t, data.latitude, data.longitude, ayanamsa)
    return positions, float(asc_sid)


@router.post("/matching")
async def compute_matching(data: MatchingData):
    """
    Kundali Matching: Ashta Koota Milan & Dashakoota Poruthams.
    
    Compares the birth charts of bride and groom across compatibility
    factors depending on the selected system ('north_indian', 'south_indian', 'both').
    """
    try:
        # Compute chart data for both individuals
        bride_planets, bride_asc = _compute_person(data.bride)
        groom_planets, groom_asc = _compute_person(data.groom)

        # Extract Moon sidereal longitudes
        bride_moon_lon = bride_planets['Moon']['sidereal_longitude']
        groom_moon_lon = groom_planets['Moon']['sidereal_longitude']

        # Compute Kundali Matching
        result = compute_kundali_matching(
            bride_moon_lon=bride_moon_lon,
            groom_moon_lon=groom_moon_lon,
            bride_planets=bride_planets,
            groom_planets=groom_planets,
            bride_asc_sid=bride_asc,
            groom_asc_sid=groom_asc,
            bride_birth_date=data.bride.date,
            groom_birth_date=data.groom.date,
            system=data.system
        )

        return sanitize_numpy(result)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
