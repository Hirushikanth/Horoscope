"""
stars.py — Fixed Stars Catalog for Vedic Astrology
=====================================================
Curated catalog of astrologically important stars including all 27 Yogatara
(junction stars of Nakshatras) and major navigational/astrological stars.
Uses Hipparcos catalog via Skyfield with proper motion correction.
"""

import numpy as np
from skyfield.api import Star
import math

# ═══════════════════════════════════════════════════════════════════════════ #
# IMPORTANT FIXED STARS — Hipparcos IDs + J2000 coordinates
# ═══════════════════════════════════════════════════════════════════════════ #
# Each entry: (HIP_ID, english_name, sanskrit_name, nakshatra, ra_hours, dec_deg, mag,
#              ra_pm_mas/yr, dec_pm_mas/yr, parallax_mas)

STAR_CATALOG = [
    # 27 Yogatara (Junction Stars of each Nakshatra)
    (7588,   "Beta Arietis",      "Ashwini",           "Ashwini",          2.1066,   20.8083,  2.64,  98.74,  -110.41, 27.30),
    (14576,  "35 Arietis",        "Bharani",           "Bharani",          3.1380,   27.6707,  4.66,  75.93,  -51.90,  13.52),
    (21421,  "Aldebaran",         "Rohini",            "Rohini",           4.5987,   16.5093,  0.85,  62.78,  -189.36, 50.09),
    (17702,  "Alcyone",           "Krittika",          "Krittika",         3.7914,   24.1050,  2.87,  19.35,  -43.11,  8.87),
    (28360,  "Lambda Orionis",    "Mrigashira",        "Mrigashira",       5.5853,   9.9342,   3.54,  -1.69,  -0.81,   3.09),
    (32349,  "Betelgeuse",        "Ardra",             "Ardra",            5.9195,   7.4070,   0.42,  27.33,  10.86,   6.55),
    (36850,  "Pollux",            "Punarvasu",         "Punarvasu",        7.7553,   28.0262,  1.14,  -625.69, -45.95, 96.54),
    (37826,  "Delta Cancri",      "Pushya",            "Pushya",           8.7446,   18.1542,  3.94,  -17.67, -228.51, 24.55),
    (45941,  "Epsilon Hydrae",    "Ashlesha",          "Ashlesha",         8.7798,   6.4189,   3.38,  -49.54, 17.67,   21.07),
    (49669,  "Regulus",           "Magha",             "Magha",            10.1395,  11.9672,  1.35,  -249.40, 4.91,   42.09),
    (54872,  "Delta Leonis",      "Purva Phalguni",    "Purva Phalguni",   11.2351,  20.5238,  2.56,  -131.30, -130.43, 55.82),
    (57632,  "Denebola",          "Uttara Phalguni",   "Uttara Phalguni",  11.8177,  14.5720,  2.14,  -499.02, -113.78, 90.16),
    (62956,  "Delta Corvi",       "Hasta",             "Hasta",            12.4977,  -16.5163, 2.95,  -210.49, -138.74, 37.11),
    (65474,  "Spica",             "Chitra",            "Chitra",           13.4199,  -11.1613, 0.97,  -42.50,  -31.73,  12.44),
    (71683,  "Arcturus",          "Swati",             "Swati",            14.2612,  19.1824,  -0.05, -1093.45,-1999.40,88.85),
    (76333,  "Alpha Librae",      "Vishakha",          "Vishakha",         14.8480,  -16.0418, 2.75,  -105.69, -69.00, 42.24),
    (80763,  "Delta Scorpii",     "Anuradha",          "Anuradha",         16.0055,  -22.6217, 2.32,  -10.21,  -36.90, 6.64),
    (80112,  "Antares",           "Jyeshtha",          "Jyeshtha",         16.4901,  -26.4320, 0.96,  -10.16,  -23.21, 5.89),
    (86228,  "Lambda Scorpii",    "Moola",             "Moola",            17.5602,  -37.1038, 1.63,  -8.90,   -29.95, 5.71),
    (90185,  "Delta Sagittarii",  "Purva Ashadha",     "Purva Ashadha",    18.3499,  -29.8281, 2.70,  32.54,   -25.76, 9.38),
    (93506,  "Sigma Sagittarii",  "Uttara Ashadha",    "Uttara Ashadha",   18.9211,  -26.2967, 2.05,  15.14,   -53.43, 14.54),
    (95947,  "Alpha Lyrae",       "Shravana",          "Shravana",         18.6156,  38.7837,  0.03,  201.02,  286.23, 130.23),
    (97649,  "Beta Delphini",     "Dhanishta",         "Dhanishta",        20.6258,  14.5953,  3.63,  118.06,  -47.18, 33.48),
    (99473,  "Lambda Aquarii",    "Shatabhisha",       "Shatabhisha",      22.8768,  -7.5797,  3.74,  -17.87,  33.37,  8.14),
    (106278, "Alpha Pegasi",      "Purva Bhadrapada",  "Purva Bhadrapada", 23.0796,  15.2053,  2.49,  61.10,   -42.18, 33.18),
    (1067,   "Gamma Pegasi",      "Uttara Bhadrapada", "Uttara Bhadrapada",0.2205,   15.1836,  2.83,  0.23,    -6.61,  8.20),
    (5447,   "Zeta Piscium",      "Revati",            "Revati",           1.2282,   7.5850,   5.24,  84.40,   19.56,  11.85),

    # Major Navigational & Astrological Stars (non-Yogatara)
    (32349,  "Betelgeuse",  "Arudra",     "Ardra",     5.9195,   7.4070,   0.42,  27.33,  10.86,  6.55),
    (24436,  "Rigel",       "Riksha",     "-",         5.2423,  -8.2017,   0.13, 1.87,   -0.56,  3.78),
    (30438,  "Canopus",     "Agastya",    "-",         6.3992, -52.6957,  -0.74, 19.99,  23.67,  10.55),
    (32349,  "Sirius",      "Mrgavyadha", "-",         6.7525, -16.7161,  -1.46, -546.01,-1223.07,379.21),
    (69673,  "Arcturus",    "Svati",      "Swati",    14.2612,  19.1824,  -0.05, -1093.45,-1999.40,88.85),
    (91262,  "Vega",        "Abhijit",    "-",        18.6156,  38.7837,   0.03, 201.02, 286.23, 130.23),
    (24608,  "Capella",     "Brahma Hridaya","-",      5.2783,  45.9980,   0.08, 75.52,  -427.13,77.29),
    (27989,  "Bellatrix",   "Kakshi",     "-",         5.4185,   6.3496,   1.64, -8.75,  -13.28, 12.92),
    (113368, "Fomalhaut",   "Hasta Mina", "-",        22.9607, -29.6222,   1.16, 329.22, -164.22,130.08),
]


def get_star_positions(t, ayanamsa: float, observer=None) -> list:
    """
    Compute ecliptic positions for all catalog stars at time t.
    Applies proper motion correction and converts to sidereal coordinates.

    Parameters:
        t: Skyfield Time object
        ayanamsa: Current Lahiri Ayanamsa in degrees
        observer: Optional Skyfield observer (Earth + Topos)

    Returns:
        List of star dicts with ecliptic and equatorial coordinates.
    """
    from ephemeris import load_ephemeris
    _, eph = load_ephemeris()
    earth = eph['earth']

    if observer is None:
        observer = earth

    seen_hips = set()
    stars = []

    for entry in STAR_CATALOG:
        hip_id, eng_name, san_name, nak, ra_h, dec_d, mag, ra_pm, dec_pm, plx = entry

        if hip_id in seen_hips:
            continue
        seen_hips.add(hip_id)

        star_obj = Star(
            ra_hours=np.float64(ra_h),
            dec_degrees=np.float64(dec_d),
            ra_mas_per_year=np.float64(ra_pm),
            dec_mas_per_year=np.float64(dec_pm),
            parallax_mas=np.float64(plx),
        )

        astrometric = observer.at(t).observe(star_obj)

        # Equatorial coordinates
        ra, dec, _ = astrometric.radec()

        # Ecliptic coordinates
        ecl_lat, ecl_lon, _ = astrometric.ecliptic_latlon(epoch='date')
        trop_lon = np.float64(ecl_lon.degrees)
        sid_lon = trop_lon - np.float64(ayanamsa)
        if sid_lon < np.float64(0.0):
            sid_lon += np.float64(360.0)

        # Determine which rashi the star falls in
        rashi_index = int(sid_lon / np.float64(30.0))
        rashi_names = ["Mesha", "Vrishabha", "Mithuna", "Karka", "Simha", "Kanya",
                       "Tula", "Vrischika", "Dhanu", "Makara", "Kumbha", "Meena"]

        stars.append({
            'hip_id': hip_id,
            'name': eng_name,
            'sanskrit_name': san_name,
            'associated_nakshatra': nak,
            'magnitude': mag,
            'ra_hours': float(ra.hours),
            'dec_degrees': float(dec.degrees),
            'tropical_longitude': float(trop_lon),
            'sidereal_longitude': float(sid_lon),
            'ecliptic_latitude': float(ecl_lat.degrees),
            'rashi': rashi_names[rashi_index] if rashi_index < 12 else "Unknown",
        })

    # Sort by magnitude (brightest first)
    stars.sort(key=lambda s: s['magnitude'])
    return stars
