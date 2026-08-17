"""
stars.py — Hipparcos yogatara catalog with proper-motion corrected positions.

The **yogataras** are the 27 junction stars marking the start of each
Nakshatra in classical Hindu astronomy; together they anchor the
sidereal zodiac itself (Chitra = Spica is fixed at 180° sidereal by the
Chitrapaksha definition). A small set of major navigation stars
(Sirius, Canopus, Abhijit/Vega, ...) is included alongside.

Catalog data (J2000/ICRS right ascension, declination, proper motion,
parallax, magnitude) is transcribed from the ESA Hipparcos main
catalogue (Perryman et al. 1997; ``I/239/hip_main``) so that positions
propagate to the query date with full proper-motion correction —
essential for high-PM yogataras such as Swati/Arcturus (~2.2″/yr).

References:
    - Perryman et al. 1997, "The Hipparcos Catalogue" (ESA SP-1200)
    - docs/01-thirukanitha-jathakam-calculation.md  §2 (Chitrapaksha)
    - Meeus, "Astronomical Algorithms" (2nd ed.), ch. 12 (precession/PM)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

import numpy as np
from skyfield.starlib import Star
from skyfield.timelib import Time

from app.astronomy.ayanamsa import SPICA, tropical_to_sidereal
from app.core.ephemeris_loader import get_earth

# ═══════════════════════════════════════════════════════════════════════ #
# Catalog record
# ═══════════════════════════════════════════════════════════════════════ #


@dataclass(frozen=True)
class StarCatalogEntry:
    """One entry of the embedded Hipparcos yogatara catalog.

    Attributes:
        hip_id: Hipparcos catalogue identifier.
        name: Common English name.
        designation: Bayer/Flamsteed designation (e.g. ``Beta Arietis``).
        sanskrit_name: Sanskrit star name, or ``None`` when not attested.
        associated_nakshatra_index: 0-based index of the Nakshatra this
            yogatara marks (``None`` for non-yogatara stars).
        magnitude: Visual magnitude (Hipparcos ``Vmag``).
        ra_degrees: ICRS right ascension at J2000 epoch, degrees.
        dec_degrees: ICRS declination at J2000 epoch, degrees.
        ra_proper_motion: Proper motion in RA, mas/year.
        dec_proper_motion: Proper motion in Dec, mas/year.
        parallax_mas: Annual parallax, mas.
    """

    hip_id: int
    name: str
    designation: str
    sanskrit_name: str | None
    associated_nakshatra_index: int | None
    magnitude: float
    ra_degrees: float
    dec_degrees: float
    ra_proper_motion: float
    dec_proper_motion: float
    parallax_mas: float


# ═══════════════════════════════════════════════════════════════════════ #
# The 27 Yogataras + major navigation stars
# ═══════════════════════════════════════════════════════════════════════ #
# RA/Dec are ICRS J2000 (degrees); proper motion in mas/yr; parallax in
# mas — all from the Hipparcos main catalogue (I/239/hip_main).
# The nakshatra index follows the same 0-based ordering as
# ``app.vedic.tables.NAKSHATRA_NAMES`` (Ashwini = 0 ... Revati = 26).

STAR_CATALOG: tuple[StarCatalogEntry, ...] = (
    StarCatalogEntry(
        8903,
        "Sheratan",
        "Beta Arietis",
        "Aśvinī",
        0,
        2.64,
        28.65978771,
        20.80829949,
        96.32,
        -108.8,
        54.74,
    ),
    StarCatalogEntry(
        14576,
        "35 Arietis",
        "35 Arietis",
        "Bharaṇī",
        1,
        2.09,
        47.04220716,
        40.9556512,
        2.39,
        -1.44,
        35.14,
    ),
    StarCatalogEntry(
        17702,
        "Alcyone",
        "Eta Tauri",
        "Kṛttikā",
        2,
        2.85,
        56.87110065,
        24.10524193,
        19.35,
        -43.11,
        8.87,
    ),
    StarCatalogEntry(
        21421,
        "Aldebaran",
        "Alpha Tauri",
        "Rohiṇī",
        3,
        0.87,
        68.98000195,
        16.50976164,
        62.78,
        -189.36,
        50.09,
    ),
    StarCatalogEntry(
        27366,
        "Meissa",
        "Lambda Orionis",
        "Mṛgaśirā",
        4,
        2.07,
        86.93911641,
        -9.66960186,
        1.55,
        -1.2,
        4.52,
    ),
    StarCatalogEntry(
        27989,
        "Betelgeuse",
        "Alpha Orionis",
        "Ārdrā",
        5,
        0.45,
        88.79287161,
        7.40703634,
        27.33,
        10.86,
        7.63,
    ),
    StarCatalogEntry(
        37826,
        "Pollux",
        "Beta Geminorum",
        "Punarvasū",
        6,
        1.16,
        116.33068263,
        28.02631031,
        -625.69,
        -45.95,
        96.74,
    ),
    StarCatalogEntry(
        42911,
        "Asellus Australis",
        "Delta Cancri",
        "Puṣyā",
        7,
        3.94,
        131.17129209,
        18.15486399,
        -17.1,
        -228.46,
        23.97,
    ),
    StarCatalogEntry(
        43109,
        "Ashlesha",
        "Epsilon Hydrae",
        "Āśleṣā",
        8,
        3.38,
        131.6943593,
        6.41890691,
        -231.04,
        -40.17,
        24.13,
    ),
    StarCatalogEntry(
        49669,
        "Regulus",
        "Alpha Leonis",
        "Maghā",
        9,
        1.36,
        152.09358075,
        11.96719513,
        -249.4,
        4.91,
        42.09,
    ),
    StarCatalogEntry(
        54872,
        "Zosma",
        "Delta Leonis",
        "Pūrvā Phalgunī",
        10,
        2.56,
        168.52671705,
        20.52403384,
        143.31,
        -130.43,
        56.52,
    ),
    StarCatalogEntry(
        57632,
        "Denebola",
        "Beta Leonis",
        "Uttarā Phalgunī",
        11,
        2.14,
        177.26615977,
        14.57233687,
        -499.02,
        -113.78,
        90.16,
    ),
    StarCatalogEntry(
        60965,
        "Algorab",
        "Delta Corvi",
        "Hastā",
        12,
        2.94,
        187.4665965,
        -16.51509397,
        -209.97,
        -139.3,
        37.11,
    ),
    StarCatalogEntry(
        65474,
        "Spica",
        "Alpha Virginis",
        "Citrā",
        13,
        0.98,
        201.2983523,
        -11.16124491,
        -42.5,
        -31.73,
        12.44,
    ),
    StarCatalogEntry(
        69673,
        "Arcturus",
        "Alpha Boötis",
        "Svātī",
        14,
        -0.05,
        213.91811403,
        19.18726997,
        -1093.45,
        -1999.4,
        88.85,
    ),
    StarCatalogEntry(
        72622,
        "Zubenelgenubi",
        "Alpha Librae",
        "Viśākhā",
        15,
        2.75,
        222.71990536,
        -16.04161047,
        -105.69,
        -69.0,
        42.25,
    ),
    StarCatalogEntry(
        78401,
        "Dschubba",
        "Delta Scorpii",
        "Anurādhā",
        16,
        2.29,
        240.08338225,
        -22.62162024,
        -8.67,
        -36.9,
        8.12,
    ),
    StarCatalogEntry(
        80763,
        "Antares",
        "Alpha Scorpii",
        "Jyeṣṭhā",
        17,
        1.06,
        247.35194804,
        -26.43194608,
        -10.16,
        -23.21,
        5.4,
    ),
    StarCatalogEntry(
        85927,
        "Shaula",
        "Lambda Scorpii",
        "Mūla",
        18,
        1.62,
        263.40219373,
        -37.10374835,
        -8.9,
        -29.95,
        4.64,
    ),
    StarCatalogEntry(
        89931,
        "Kaus Media",
        "Delta Sagittarii",
        "Pūrvāṣāḍhā",
        19,
        2.72,
        275.24842337,
        -29.82803914,
        29.96,
        -26.38,
        10.67,
    ),
    StarCatalogEntry(
        90496,
        "Nunki",
        "Sigma Sagittarii",
        "Uttarāṣāḍhā",
        20,
        2.82,
        276.99278955,
        -25.42124732,
        -44.81,
        -186.29,
        42.2,
    ),
    StarCatalogEntry(
        97649,
        "Altair",
        "Alpha Aquilae",
        "Śravaṇa",
        21,
        0.76,
        297.6945086,
        8.86738491,
        536.82,
        385.54,
        194.44,
    ),
    StarCatalogEntry(
        102281,
        "Rotanev",
        "Beta Delphini",
        "Dhaniṣṭhā",
        22,
        4.43,
        310.86477381,
        15.07468224,
        -19.61,
        -41.74,
        16.03,
    ),
    StarCatalogEntry(
        112961,
        "Hydor",
        "Lambda Aquarii",
        "Śatabhiṣā",
        23,
        3.73,
        343.15360192,
        -7.57967878,
        19.51,
        32.71,
        8.33,
    ),
    StarCatalogEntry(
        113963,
        "Markab",
        "Alpha Pegasi",
        "Pūrvā Bhādrapadā",
        24,
        2.49,
        346.1900702,
        15.20536786,
        61.1,
        -42.56,
        23.36,
    ),
    StarCatalogEntry(
        1067,
        "Algenib",
        "Gamma Pegasi",
        "Uttarā Bhādrapadā",
        25,
        2.83,
        3.30895828,
        15.18361593,
        4.7,
        -8.24,
        9.79,
    ),
    StarCatalogEntry(
        573,
        "Zeta Piscium",
        "Zeta Piscium",
        "Revatī",
        26,
        7.62,
        1.73459748,
        -43.98527,
        41.23,
        16.72,
        3.73,
    ),
    # ── Major navigation stars (non-yogatara) ────────────────────────── #
    StarCatalogEntry(
        91262,
        "Vega",
        "Alpha Lyrae",
        "Abhijit",
        None,
        0.03,
        279.23410832,
        38.78299311,
        201.02,
        287.46,
        128.93,
    ),
    StarCatalogEntry(
        32349,
        "Sirius",
        "Alpha Canis Majoris",
        "Lubdhaka",
        None,
        -1.44,
        101.28854105,
        -16.71314306,
        -546.01,
        -1223.08,
        379.21,
    ),
    StarCatalogEntry(
        30438,
        "Canopus",
        "Alpha Carinae",
        "Agastya",
        None,
        -0.62,
        95.98787763,
        -52.69571799,
        19.99,
        23.67,
        10.43,
    ),
    StarCatalogEntry(
        24436,
        "Rigel",
        "Beta Orionis",
        "Triśaṅku",
        None,
        0.18,
        78.63446353,
        -8.20163919,
        1.87,
        -0.56,
        4.22,
    ),
    StarCatalogEntry(
        24608,
        "Capella",
        "Alpha Aurigae",
        "Brahmahṛdaya",
        None,
        0.08,
        79.17206517,
        45.99902927,
        75.52,
        -427.13,
        77.29,
    ),
    StarCatalogEntry(
        113368,
        "Fomalhaut",
        "Alpha Piscis Austrini",
        "Hasta Mina",
        None,
        1.17,
        344.41177323,
        -29.62183701,
        329.22,
        -164.22,
        130.08,
    ),
    StarCatalogEntry(
        11767,
        "Polaris",
        "Alpha Ursae Minoris",
        "Dhruva",
        None,
        1.97,
        37.94614689,
        89.26413805,
        44.22,
        -11.74,
        7.56,
    ),
    StarCatalogEntry(
        7588,
        "Achernar",
        "Alpha Eridani",
        "Agni Sthamba",
        None,
        0.45,
        24.42813204,
        -57.23666007,
        88.02,
        -40.08,
        22.68,
    ),
    StarCatalogEntry(
        37279,
        "Procyon",
        "Alpha Canis Minoris",
        "Mṛgavyādha",
        None,
        0.4,
        114.82724194,
        5.22750767,
        -716.57,
        -1034.58,
        285.93,
    ),
)

#: The number of degrees in one Nakshatra (360° / 27).
NAKSHATRA_SPAN_DEG: np.float64 = np.float64(360.0) / np.float64(27.0)

#: One astronomical unit expressed in light years (for distance display).
AU_IN_LIGHT_YEARS: np.float64 = np.float64(1.581250740518e-5)

#: The Hipparcos identifier of Chitra (Spica) — the Chitrapaksha anchor.
CHITRA_HIP_ID: int = 65474

# ═══════════════════════════════════════════════════════════════════════ #
# Position computation
# ═══════════════════════════════════════════════════════════════════════ #


@dataclass(frozen=True)
class StarPosition:
    """A catalog star's full position state at a given instant.

    Attributes:
        entry: The catalog record the position was computed from.
        ra_hours: Apparent right ascension, hours.
        dec_degrees: Apparent declination, degrees.
        tropical_longitude: True-of-date tropical ecliptic longitude, degrees.
        sidereal_longitude: Nirayana (Lahiri) longitude, degrees.
        ecliptic_latitude: True-of-date ecliptic latitude, degrees.
        distance_light_years: Geocentric distance, light years.
    """

    entry: StarCatalogEntry
    ra_hours: np.float64
    dec_degrees: np.float64
    tropical_longitude: np.float64
    sidereal_longitude: np.float64
    ecliptic_latitude: np.float64
    distance_light_years: np.float64


def _to_star(entry: StarCatalogEntry) -> Star:
    """Build a proper-motion-aware Skyfield ``Star`` from a catalog entry.

    Hipparcos positions are J2000 (ICRS); Skyfield propagates them to
    the observation date using the embedded proper motion and parallax.
    Chitra (Spica) reuses the exact ``SPICA`` definition of the ayanamsa
    anchor so that the catalog reproduces ``Sidereal(Chitra) ≡ 180°`` —
    the Chitrapaksha trust invariant.
    """
    if entry.hip_id == CHITRA_HIP_ID:
        return SPICA
    return Star(
        ra_hours=np.float64(entry.ra_degrees) / np.float64(15.0),
        dec_degrees=np.float64(entry.dec_degrees),
        ra_mas_per_year=np.float64(entry.ra_proper_motion),
        dec_mas_per_year=np.float64(entry.dec_proper_motion),
        parallax_mas=np.float64(entry.parallax_mas),
    )


def get_star_positions(
    t: Time,
    ayanamsa: np.float64,
    *,
    node_convention: Literal["mean", "true"] = "mean",
) -> list[StarPosition]:
    """Apparent positions of every catalog star at instant ``t``.

    Proper motion is applied by Skyfield from the J2000 catalog epoch to
    ``t``; the ecliptic longitude is then converted to the sidereal
    (nirayana) frame with the given Lahiri ayanamsa.

    Parameters:
        t: Skyfield time of observation.
        ayanamsa: Ayanamsa value, degrees.
        node_convention: Accepted for API parity; does not affect stars.

    Returns:
        One ``StarPosition`` per catalog entry, sorted by magnitude
        (brightest first).
    """
    del node_convention  # stars are node-independent; kept for parity
    earth = get_earth()
    stars = [_to_star(entry) for entry in STAR_CATALOG]

    positions: list[StarPosition] = []
    for entry, star in zip(STAR_CATALOG, stars, strict=True):
        astrometric = earth.at(t).observe(star)
        ra, dec, distance = astrometric.radec()
        ecl_lat, ecl_lon, _ = astrometric.ecliptic_latlon(epoch="date")

        tropical = np.float64(ecl_lon.degrees)
        positions.append(
            StarPosition(
                entry=entry,
                ra_hours=np.float64(ra.hours),
                dec_degrees=np.float64(dec.degrees),
                tropical_longitude=tropical,
                sidereal_longitude=tropical_to_sidereal(tropical, ayanamsa),
                ecliptic_latitude=np.float64(ecl_lat.degrees),
                distance_light_years=np.float64(distance.au) * AU_IN_LIGHT_YEARS,
            )
        )

    positions.sort(key=lambda p: p.entry.magnitude)
    return positions


def nakshatra_index_of(sidereal_longitude: np.float64) -> int:
    """0-based Nakshatra index a sidereal longitude currently falls in.

    Kept here (not in the Vedic layer) because it is plain zodiac
    arithmetic shared by the star catalogue.
    """
    return int(np.float64(sidereal_longitude) // NAKSHATRA_SPAN_DEG) % 27
