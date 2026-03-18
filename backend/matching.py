"""
matching.py — Kundali Matching (Ashta Koota Milan) Module
============================================================
Implements the complete 36-point Ashta Koota compatibility system
for Vedic marriage matching. Compares the Moon's Nakshatra and Rashi
of bride and groom across 8 factors, plus Manglik Dosha and Vedha checks.

All computations in IEEE 754 float64 precision.

The Eight Kootas (Compatibility Factors):
    1. Varna   (1 pt)  — Spiritual/ego compatibility
    2. Vashya  (2 pts) — Mutual attraction and influence
    3. Tara    (3 pts) — Star harmony and destiny alignment
    4. Yoni    (4 pts) — Physical/sexual compatibility
    5. Graha Maitri (5 pts) — Planetary friendship (mental harmony)
    6. Gana    (6 pts) — Temperamental compatibility
    7. Bhakoot (7 pts) — Emotional and family harmony
    8. Nadi    (8 pts) — Genetic and health compatibility

References:
    - Brihat Parashara Hora Shastra (BPHS), Ch. 79-80
    - Muhurta Chintamani by Daivagna Rama
    - Jataka Parijata by Vaidyanatha Dikshita
    - Phaldeepika by Mantreswara, Ch. 7
"""

import numpy as np
from vedic import (
    NAKSHATRAS, RASHIS, get_nakshatra, get_rashi,
    get_bhava, get_planetary_dignity,
)


# ═══════════════════════════════════════════════════════════════════════════ #
# VARNA KOOTA — Spiritual Compatibility (Max 1 point)
# ═══════════════════════════════════════════════════════════════════════════ #
# Varnas ranked: Brahmin(1) > Kshatriya(2) > Vaishya(3) > Shudra(4)
# Rashi-based mapping (North Indian / Uttar Bharat tradition):
#   Brahmin : Cancer(4), Scorpio(8), Pisces(12) — Water signs
#   Kshatriya: Aries(1), Leo(5), Sagittarius(9) — Fire signs
#   Vaishya : Taurus(2), Virgo(6), Capricorn(10) — Earth signs
#   Shudra  : Gemini(3), Libra(7), Aquarius(11) — Air signs

# Index 0-11 corresponds to Rashi index 0-11 (Mesha=0 ... Meena=11)
# Value = Varna rank: 1=Brahmin, 2=Kshatriya, 3=Vaishya, 4=Shudra
VARNA_BY_RASHI: list[int] = [
    2,  # 0  Mesha     (Aries)       — Kshatriya
    3,  # 1  Vrishabha (Taurus)      — Vaishya
    4,  # 2  Mithuna   (Gemini)      — Shudra
    1,  # 3  Karka     (Cancer)      — Brahmin
    2,  # 4  Simha     (Leo)         — Kshatriya
    3,  # 5  Kanya     (Virgo)       — Vaishya
    4,  # 6  Tula      (Libra)       — Shudra
    1,  # 7  Vrischika (Scorpio)     — Brahmin
    2,  # 8  Dhanu     (Sagittarius) — Kshatriya
    3,  # 9  Makara    (Capricorn)   — Vaishya
    4,  # 10 Kumbha    (Aquarius)    — Shudra
    1,  # 11 Meena     (Pisces)      — Brahmin
]

VARNA_NAMES: dict[int, str] = {
    1: "Brahmin", 2: "Kshatriya", 3: "Vaishya", 4: "Shudra"
}


# ═══════════════════════════════════════════════════════════════════════════ #
# VASHYA KOOTA — Mutual Attraction & Influence (Max 2 points)
# ═══════════════════════════════════════════════════════════════════════════ #
# Five Vashya types:
#   Chatushpada (Quadruped) : Aries, Taurus, 2nd half Sagittarius,
#                              1st half Capricorn
#   Manav (Human)           : Gemini, Virgo, Libra, 1st half Sagittarius,
#                              Aquarius
#   Jalchar (Aquatic)       : Cancer, Pisces, 2nd half Capricorn
#   Vanchar (Wild/Forest)   : Leo
#   Keeta (Insect/Reptile)  : Scorpio
#
# For simplicity, each Rashi maps to its primary Vashya category.
# Sagittarius primary = Manav, Capricorn primary = Chatushpada.

VASHYA_TYPES: dict[str, int] = {
    "Chatushpada": 0, "Manav": 1, "Jalchar": 2, "Vanchar": 3, "Keeta": 4
}

VASHYA_BY_RASHI: list[str] = [
    "Chatushpada",  # 0  Mesha     (Aries)
    "Chatushpada",  # 1  Vrishabha (Taurus)
    "Manav",        # 2  Mithuna   (Gemini)
    "Jalchar",      # 3  Karka     (Cancer)
    "Vanchar",      # 4  Simha     (Leo)
    "Manav",        # 5  Kanya     (Virgo)
    "Manav",        # 6  Tula      (Libra)
    "Keeta",        # 7  Vrischika (Scorpio)
    "Manav",        # 8  Dhanu     (Sagittarius)
    "Chatushpada",  # 9  Makara    (Capricorn)
    "Manav",        # 10 Kumbha    (Aquarius)
    "Jalchar",      # 11 Meena     (Pisces)
]

# Vashya compatibility scoring matrix [bride_type][groom_type]
# Order: Chatushpada(0), Manav(1), Jalchar(2), Vanchar(3), Keeta(4)
# 2 = full compatibility, 1 = partial, 0.5 = low, 0 = no compatibility
VASHYA_COMPAT: list[list[float]] = [
    # Chat  Manav  Jalch  Vanch  Keeta
    [2.0,   0.5,   1.0,   0.0,   0.0],   # Chatushpada
    [0.5,   2.0,   0.0,   0.5,   1.0],   # Manav
    [1.0,   0.0,   2.0,   0.0,   0.5],   # Jalchar
    [0.0,   0.5,   0.0,   2.0,   1.0],   # Vanchar
    [0.0,   1.0,   0.5,   1.0,   2.0],   # Keeta
]


# ═══════════════════════════════════════════════════════════════════════════ #
# YONI KOOTA — Physical/Sexual Compatibility (Max 4 points)
# ═══════════════════════════════════════════════════════════════════════════ #
# 14 animal types, each Nakshatra maps to one animal.
# Each animal has a male and female Nakshatra.

# Nakshatra index (0-26) → animal name
YONI_BY_NAKSHATRA: list[str] = [
    "Horse",     # 0  Ashwini
    "Elephant",  # 1  Bharani
    "Goat",      # 2  Krittika
    "Serpent",   # 3  Rohini
    "Serpent",   # 4  Mrigashira
    "Dog",       # 5  Ardra
    "Cat",       # 6  Punarvasu
    "Goat",      # 7  Pushya
    "Cat",       # 8  Ashlesha
    "Rat",       # 9  Magha
    "Rat",       # 10 Purva Phalguni
    "Cow",       # 11 Uttara Phalguni
    "Buffalo",   # 12 Hasta
    "Tiger",     # 13 Chitra
    "Buffalo",   # 14 Swati
    "Tiger",     # 15 Vishakha
    "Deer",      # 16 Anuradha
    "Deer",      # 17 Jyeshtha
    "Dog",       # 18 Moola
    "Monkey",    # 19 Purva Ashadha
    "Mongoose",  # 20 Uttara Ashadha
    "Monkey",    # 21 Shravana
    "Lion",      # 22 Dhanishta
    "Horse",     # 23 Shatabhisha
    "Lion",      # 24 Purva Bhadrapada
    "Cow",       # 25 Uttara Bhadrapada
    "Elephant",  # 26 Revati
]

# All 14 animal names in a fixed order for the compatibility matrix
_YONI_ANIMAL_ORDER: list[str] = [
    "Horse", "Elephant", "Goat", "Serpent", "Dog", "Cat", "Rat",
    "Cow", "Buffalo", "Tiger", "Deer", "Monkey", "Mongoose", "Lion"
]
_YONI_ANIMAL_IDX: dict[str, int] = {a: i for i, a in enumerate(_YONI_ANIMAL_ORDER)}

# 14×14 Yoni compatibility matrix
# 4 = Same yoni (best), 3 = Friendly, 2 = Neutral, 1 = Unfriendly, 0 = Enemy
# Reference: Muhurta Chintamani, Jataka Parijata
YONI_COMPAT_MATRIX: list[list[int]] = [
    # Hors  Elep  Goat  Serp  Dog   Cat   Rat   Cow   Buf   Tigr  Deer  Monk  Mong  Lion
    [4,     2,    2,    3,    2,    2,    2,    1,    0,    1,    3,    2,    2,    1],  # Horse
    [2,     4,    3,    3,    2,    2,    2,    2,    3,    1,    2,    3,    2,    0],  # Elephant
    [2,     3,    4,    2,    2,    2,    1,    3,    2,    0,    2,    3,    2,    2],  # Goat
    [3,     3,    2,    4,    2,    1,    1,    1,    1,    2,    2,    2,    0,    2],  # Serpent
    [2,     2,    2,    2,    4,    2,    1,    2,    2,    1,    0,    2,    1,    2],  # Dog
    [2,     2,    2,    1,    2,    4,    0,    2,    2,    2,    3,    2,    1,    2],  # Cat
    [2,     2,    1,    1,    1,    0,    4,    2,    2,    2,    2,    2,    1,    2],  # Rat
    [1,     2,    3,    1,    2,    2,    2,    4,    3,    0,    2,    2,    2,    1],  # Cow
    [0,     3,    2,    1,    2,    2,    2,    3,    4,    1,    2,    1,    1,    2],  # Buffalo
    [1,     1,    0,    2,    1,    2,    2,    0,    1,    4,    1,    2,    2,    3],  # Tiger
    [3,     2,    2,    2,    0,    3,    2,    2,    2,    1,    4,    2,    2,    1],  # Deer
    [2,     3,    3,    2,    2,    2,    2,    2,    1,    2,    2,    4,    2,    2],  # Monkey
    [2,     2,    2,    0,    1,    1,    1,    2,    1,    2,    2,    2,    4,    2],  # Mongoose
    [1,     0,    2,    2,    2,    2,    2,    1,    2,    3,    1,    2,    2,    4],  # Lion
]


# ═══════════════════════════════════════════════════════════════════════════ #
# GRAHA MAITRI KOOTA — Planetary Friendship (Max 5 points)
# ═══════════════════════════════════════════════════════════════════════════ #
# Naisargika (natural) planetary friendships as per BPHS Chapter 3.
# F = Friend, N = Neutral, E = Enemy

_GRAHA_PLANETS: list[str] = [
    "Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"
]
_GRAHA_IDX: dict[str, int] = {p: i for i, p in enumerate(_GRAHA_PLANETS)}

# Friendship matrix: _GRAHA_MAITRI[planet_a_idx][planet_b_idx]
# Values: 1 = Friend, 0 = Neutral, -1 = Enemy
GRAHA_MAITRI: list[list[int]] = [
    # Sun  Moon  Mars  Merc  Jup   Ven   Sat
    [ 0,   1,    1,   -1,    1,   -1,   -1],  # Sun
    [ 1,   0,    0,    0,    1,    0,    0],  # Moon
    [ 1,   1,    0,    0,    1,   -1,   -1],  # Mars
    [-1,   0,    0,    0,   -1,    1,    1],  # Mercury
    [ 1,   1,    1,   -1,    0,   -1,    0],  # Jupiter
    [-1,   0,   -1,    1,   -1,    0,    1],  # Venus
    [-1,   0,   -1,    1,    0,    1,    0],  # Saturn
]


# ═══════════════════════════════════════════════════════════════════════════ #
# GANA KOOTA — Temperamental Compatibility (Max 6 points)
# ═══════════════════════════════════════════════════════════════════════════ #
# Gana is already stored in NAKSHATRAS[i]["gana"] in vedic.py.
# Scoring matrix: [bride_gana][groom_gana]

_GANA_TYPES: dict[str, int] = {"Deva": 0, "Manushya": 1, "Rakshasa": 2}

# [bride_gana_idx][groom_gana_idx]
GANA_COMPAT: list[list[int]] = [
    # Deva  Manushya  Rakshasa
    [6,     5,        1],   # Bride = Deva
    [6,     6,        0],   # Bride = Manushya
    [0,     0,        6],   # Bride = Rakshasa
]


# ═══════════════════════════════════════════════════════════════════════════ #
# BHAKOOT KOOTA — Emotional & Family Harmony (Max 7 points)
# ═══════════════════════════════════════════════════════════════════════════ #
# Dosha position pairs (relative positions of bride & groom Rashi):
#   2/12  → Financial imbalance / health risk
#   5/9   → Progeny issues
#   6/8   → Severe health risk, "mrityu bhakoot"
#
# Cancellation: Same Rashi lord OR mutual friendship between lords.

BHAKOOT_DOSHA_PAIRS: set[tuple[int, int]] = {
    (2, 12), (12, 2),
    (5, 9),  (9, 5),
    (6, 8),  (8, 6),
}


# ═══════════════════════════════════════════════════════════════════════════ #
# NADI KOOTA — Genetic & Health Compatibility (Max 8 points)
# ═══════════════════════════════════════════════════════════════════════════ #
# Three Nadis cycle through the 27 Nakshatras:
#   Aadi (Vata)   → Nakshatras 1, 4, 7, 10, 13, 16, 19, 22, 25  (i % 3 == 0)
#   Madhya (Pitta) → Nakshatras 2, 5, 8, 11, 14, 17, 20, 23, 26  (i % 3 == 1)
#   Antya (Kapha)  → Nakshatras 3, 6, 9, 12, 15, 18, 21, 24, 27  (i % 3 == 2)

NADI_NAMES: list[str] = ["Aadi (Vata)", "Madhya (Pitta)", "Antya (Kapha)"]


# ═══════════════════════════════════════════════════════════════════════════ #
# VEDHA (NAKSHATRA REPULSION) — Mutually Afflicting Pairs
# ═══════════════════════════════════════════════════════════════════════════ #
# If bride and groom Nakshatras form a Vedha pair, it is inauspicious
# regardless of Koota score. Traditional pairs from Muhurta Chintamani.
# Stored as (nakshatra_index_0based, nakshatra_index_0based)

VEDHA_PAIRS: list[tuple[int, int]] = [
    (0, 17),   # Ashwini ↔ Jyeshtha
    (1, 16),   # Bharani ↔ Anuradha
    (2, 15),   # Krittika ↔ Vishakha
    (3, 14),   # Rohini ↔ Swati
    (4, 22),   # Mrigashira ↔ Dhanishta
    (5, 21),   # Ardra ↔ Shravana
    (6, 20),   # Punarvasu ↔ Uttara Ashadha
    (7, 19),   # Pushya ↔ Purva Ashadha
    (8, 18),   # Ashlesha ↔ Moola
    (9, 26),   # Magha ↔ Revati
    (10, 25),  # Purva Phalguni ↔ Uttara Bhadrapada
    (11, 24),  # Uttara Phalguni ↔ Purva Bhadrapada
    (12, 23),  # Hasta ↔ Shatabhisha
]


# ═══════════════════════════════════════════════════════════════════════════ #
# MANGLIK DOSHA — Mars Placement Check
# ═══════════════════════════════════════════════════════════════════════════ #
# Mars in houses 1, 2 (South Indian), 4, 7, 8, 12 from Lagna → Manglik.
# We include house 2 for completeness (South Indian tradition).

MANGLIK_HOUSES: set[int] = {1, 2, 4, 7, 8, 12}


# ═══════════════════════════════════════════════════════════════════════════ #
# HELPER: Get Rashi lord name from Rashi index
# ═══════════════════════════════════════════════════════════════════════════ #

def _get_rashi_lord(rashi_idx: int) -> str:
    """Return the planetary lord of a Rashi by its 0-based index."""
    return RASHIS[rashi_idx]["lord"]


def _get_nadi(nak_idx: int) -> int:
    """
    Return Nadi type (0=Aadi, 1=Madhya, 2=Antya) for a Nakshatra index (0-26).
    The Nadi cycles: Ashwini=Aadi, Bharani=Madhya, Krittika=Antya, Rohini=Aadi...
    """
    return nak_idx % 3


def _get_graha_friendship(lord_a: str, lord_b: str) -> int:
    """
    Return friendship value between two Rashi lords.
    1 = Friend, 0 = Neutral, -1 = Enemy.
    For Rahu/Ketu (shadow planets), treat as Saturn (traditional convention).
    """
    remap = {"Rahu": "Saturn", "Ketu": "Mars"}
    la = remap.get(lord_a, lord_a)
    lb = remap.get(lord_b, lord_b)
    if la not in _GRAHA_IDX or lb not in _GRAHA_IDX:
        return 0  # Fallback neutral
    return GRAHA_MAITRI[_GRAHA_IDX[la]][_GRAHA_IDX[lb]]


# ═══════════════════════════════════════════════════════════════════════════ #
# KOOTA 1: VARNA — Spiritual Compatibility (1 point)
# ═══════════════════════════════════════════════════════════════════════════ #

def calc_varna_koota(bride_rashi_idx: int, groom_rashi_idx: int) -> dict:
    """
    Varna Koota — compares spiritual compatibility based on Moon sign.

    Rule: Groom's Varna should be equal to or higher (lower number) than
    bride's Varna. If groom's Varna is lower rank → 0 points.

    Varna hierarchy: Brahmin(1) > Kshatriya(2) > Vaishya(3) > Shudra(4)

    Parameters:
        bride_rashi_idx: Bride's Moon Rashi index (0-11)
        groom_rashi_idx: Groom's Moon Rashi index (0-11)

    Returns:
        dict with obtained, max, bride_varna, groom_varna, description

    References:
        Brihat Parashara Hora Shastra, Ch. 79
    """
    bride_varna: int = VARNA_BY_RASHI[bride_rashi_idx]
    groom_varna: int = VARNA_BY_RASHI[groom_rashi_idx]
    bride_name: str = VARNA_NAMES[bride_varna]
    groom_name: str = VARNA_NAMES[groom_varna]

    # Lower number = higher rank. Groom must be >= bride in rank.
    if groom_varna <= bride_varna:
        obtained = np.float64(1.0)
        desc = f"Groom ({groom_name}) is equal or higher Varna than Bride ({bride_name})."
    else:
        obtained = np.float64(0.0)
        desc = f"Groom ({groom_name}) is lower Varna than Bride ({bride_name})."

    return {
        "obtained": float(obtained),
        "max": 1,
        "bride_varna": bride_name,
        "groom_varna": groom_name,
        "description": desc,
    }


# ═══════════════════════════════════════════════════════════════════════════ #
# KOOTA 2: VASHYA — Mutual Attraction & Influence (2 points)
# ═══════════════════════════════════════════════════════════════════════════ #

def calc_vashya_koota(bride_rashi_idx: int, groom_rashi_idx: int) -> dict:
    """
    Vashya Koota — compatibility of mutual attraction and power dynamics.

    Each Rashi belongs to one of 5 Vashya types. Scoring is based on the
    compatibility matrix between these types.

    Parameters:
        bride_rashi_idx: Bride's Moon Rashi index (0-11)
        groom_rashi_idx: Groom's Moon Rashi index (0-11)

    Returns:
        dict with obtained, max, bride_vashya, groom_vashya, description

    References:
        Muhurta Chintamani, Jataka Parijata
    """
    bride_vashya: str = VASHYA_BY_RASHI[bride_rashi_idx]
    groom_vashya: str = VASHYA_BY_RASHI[groom_rashi_idx]

    b_idx: int = VASHYA_TYPES[bride_vashya]
    g_idx: int = VASHYA_TYPES[groom_vashya]
    obtained: float = VASHYA_COMPAT[b_idx][g_idx]

    if obtained == 2.0:
        desc = f"Excellent Vashya compatibility — both {bride_vashya}." if bride_vashya == groom_vashya \
            else f"Excellent Vashya compatibility — {bride_vashya} and {groom_vashya}."
    elif obtained >= 1.0:
        desc = f"Moderate Vashya compatibility — {bride_vashya} and {groom_vashya}."
    else:
        desc = f"Low Vashya compatibility — {bride_vashya} and {groom_vashya}."

    return {
        "obtained": obtained,
        "max": 2,
        "bride_vashya": bride_vashya,
        "groom_vashya": groom_vashya,
        "description": desc,
    }


# ═══════════════════════════════════════════════════════════════════════════ #
# KOOTA 3: TARA — Star Harmony (3 points)
# ═══════════════════════════════════════════════════════════════════════════ #

def calc_tara_koota(bride_nak_idx: int, groom_nak_idx: int) -> dict:
    """
    Tara Koota — star harmony based on Nakshatra distance.

    Method:
        1. Count Nakshatras from bride to groom: (groom - bride) % 27 + 1
        2. Divide by 9, take remainder (1-9).
        3. Remainders 3 (Vipat), 5 (Pratyari), 7 (Vadha) are inauspicious.
        4. Do the same from groom to bride.
        5. Scoring:
           - Both directions auspicious → 3 points
           - One direction inauspicious → 1.5 points
           - Both directions inauspicious → 0 points

    Parameters:
        bride_nak_idx: Bride's Nakshatra index (0-26)
        groom_nak_idx: Groom's Nakshatra index (0-26)

    Returns:
        dict with obtained, max, description

    References:
        Brihat Parashara Hora Shastra, Ch. 79
    """
    INAUSPICIOUS_REMAINDERS: set[int] = {3, 5, 7}

    # Bride → Groom direction
    count_bg: int = (groom_nak_idx - bride_nak_idx) % 27 + 1
    remainder_bg: int = count_bg % 9
    if remainder_bg == 0:
        remainder_bg = 9
    bg_bad: bool = remainder_bg in INAUSPICIOUS_REMAINDERS

    # Groom → Bride direction
    count_gb: int = (bride_nak_idx - groom_nak_idx) % 27 + 1
    remainder_gb: int = count_gb % 9
    if remainder_gb == 0:
        remainder_gb = 9
    gb_bad: bool = remainder_gb in INAUSPICIOUS_REMAINDERS

    bad_count: int = int(bg_bad) + int(gb_bad)

    if bad_count == 0:
        obtained = np.float64(3.0)
        desc = "Both Tara directions are auspicious — excellent star harmony."
    elif bad_count == 1:
        obtained = np.float64(1.5)
        desc = "One Tara direction is inauspicious — moderate star harmony."
    else:
        obtained = np.float64(0.0)
        desc = "Both Tara directions are inauspicious — poor star harmony."

    return {
        "obtained": float(obtained),
        "max": 3,
        "bride_to_groom_remainder": remainder_bg,
        "groom_to_bride_remainder": remainder_gb,
        "description": desc,
    }


# ═══════════════════════════════════════════════════════════════════════════ #
# KOOTA 4: YONI — Physical/Sexual Compatibility (4 points)
# ═══════════════════════════════════════════════════════════════════════════ #

def calc_yoni_koota(bride_nak_idx: int, groom_nak_idx: int) -> dict:
    """
    Yoni Koota — physical and sexual compatibility based on animal symbols.

    Each Nakshatra is associated with one of 14 animals. Compatibility is
    checked via the 14×14 matrix.

    Scoring: 4=Same, 3=Friendly, 2=Neutral, 1=Unfriendly, 0=Enemy.

    Parameters:
        bride_nak_idx: Bride's Nakshatra index (0-26)
        groom_nak_idx: Groom's Nakshatra index (0-26)

    Returns:
        dict with obtained, max, bride_yoni, groom_yoni, description

    References:
        Muhurta Chintamani
    """
    bride_animal: str = YONI_BY_NAKSHATRA[bride_nak_idx]
    groom_animal: str = YONI_BY_NAKSHATRA[groom_nak_idx]

    b_idx: int = _YONI_ANIMAL_IDX[bride_animal]
    g_idx: int = _YONI_ANIMAL_IDX[groom_animal]
    obtained: int = YONI_COMPAT_MATRIX[b_idx][g_idx]

    YONI_LABELS: dict[int, str] = {
        4: "Same Yoni — best physical compatibility.",
        3: "Friendly Yoni — good physical compatibility.",
        2: "Neutral Yoni — average physical compatibility.",
        1: "Unfriendly Yoni — below average compatibility.",
        0: "Enemy Yoni — poor physical compatibility.",
    }
    desc = f"{bride_animal} and {groom_animal}: {YONI_LABELS[obtained]}"

    return {
        "obtained": obtained,
        "max": 4,
        "bride_yoni": bride_animal,
        "groom_yoni": groom_animal,
        "description": desc,
    }


# ═══════════════════════════════════════════════════════════════════════════ #
# KOOTA 5: GRAHA MAITRI — Planetary Friendship (5 points)
# ═══════════════════════════════════════════════════════════════════════════ #

def calc_graha_maitri_koota(bride_rashi_idx: int, groom_rashi_idx: int) -> dict:
    """
    Graha Maitri Koota — mental compatibility via Rashi lord friendship.

    Scoring based on the mutual relationship of Moon sign lords:
        Both friends        → 5 points
        One friend, one neutral → 4 points
        Both neutral        → 3 points
        One friend, one enemy   → 1 point
        One neutral, one enemy  → 0.5 points
        Both enemies        → 0 points

    Parameters:
        bride_rashi_idx: Bride's Moon Rashi index (0-11)
        groom_rashi_idx: Groom's Moon Rashi index (0-11)

    Returns:
        dict with obtained, max, bride_lord, groom_lord, description

    References:
        Brihat Parashara Hora Shastra, Ch. 3 (Naisargika Maitri)
    """
    bride_lord: str = _get_rashi_lord(bride_rashi_idx)
    groom_lord: str = _get_rashi_lord(groom_rashi_idx)

    # If both signs have the same lord, they are considered best friends
    if bride_lord == groom_lord:
        obtained = np.float64(5.0)
        desc = f"Same Rashi lord ({bride_lord}) — excellent mental compatibility."
        return {
            "obtained": float(obtained),
            "max": 5,
            "bride_lord": bride_lord,
            "groom_lord": groom_lord,
            "relationship": "Same Lord",
            "description": desc,
        }

    # Check both directions of friendship
    f_bg: int = _get_graha_friendship(bride_lord, groom_lord)
    f_gb: int = _get_graha_friendship(groom_lord, bride_lord)

    # Compound score based on mutual relationship
    total: int = f_bg + f_gb  # Range: -2 to +2

    if total >= 2:
        obtained = np.float64(5.0)
        relationship = "Mutual Friends"
        desc = f"{bride_lord} and {groom_lord} are mutual friends — excellent mental compatibility."
    elif total == 1:
        obtained = np.float64(4.0)
        relationship = "One Friend, One Neutral"
        desc = f"{bride_lord} and {groom_lord}: one considers the other a friend — good mental compatibility."
    elif total == 0 and f_bg == 0 and f_gb == 0:
        obtained = np.float64(3.0)
        relationship = "Mutually Neutral"
        desc = f"{bride_lord} and {groom_lord} are mutually neutral — average mental compatibility."
    elif total == 0:
        obtained = np.float64(1.0)
        relationship = "One Friend, One Enemy"
        desc = f"{bride_lord} and {groom_lord}: mixed friendship — below average mental compatibility."
    elif total == -1:
        obtained = np.float64(0.5)
        relationship = "One Neutral, One Enemy"
        desc = f"{bride_lord} and {groom_lord}: poor mutual regard — low mental compatibility."
    else:
        obtained = np.float64(0.0)
        relationship = "Mutual Enemies"
        desc = f"{bride_lord} and {groom_lord} are mutual enemies — poor mental compatibility."

    return {
        "obtained": float(obtained),
        "max": 5,
        "bride_lord": bride_lord,
        "groom_lord": groom_lord,
        "relationship": relationship,
        "description": desc,
    }


# ═══════════════════════════════════════════════════════════════════════════ #
# KOOTA 6: GANA — Temperamental Compatibility (6 points)
# ═══════════════════════════════════════════════════════════════════════════ #

def calc_gana_koota(bride_nak_idx: int, groom_nak_idx: int) -> dict:
    """
    Gana Koota — temperamental compatibility based on Nakshatra Gana.

    Three Ganas: Deva (divine), Manushya (human), Rakshasa (demonic).
    Same gana = 6, compatible cross = moderate, Deva×Rakshasa = 0.

    Parameters:
        bride_nak_idx: Bride's Nakshatra index (0-26)
        groom_nak_idx: Groom's Nakshatra index (0-26)

    Returns:
        dict with obtained, max, bride_gana, groom_gana, description

    References:
        Brihat Parashara Hora Shastra, Ch. 79
    """
    bride_gana: str = NAKSHATRAS[bride_nak_idx]["gana"]
    groom_gana: str = NAKSHATRAS[groom_nak_idx]["gana"]

    b_idx: int = _GANA_TYPES[bride_gana]
    g_idx: int = _GANA_TYPES[groom_gana]
    obtained: int = GANA_COMPAT[b_idx][g_idx]

    if obtained == 6:
        desc = f"Same Gana ({bride_gana}) — excellent temperamental match."
    elif obtained >= 4:
        desc = f"{bride_gana} and {groom_gana} — good temperamental compatibility."
    elif obtained >= 1:
        desc = f"{bride_gana} and {groom_gana} — some temperamental differences."
    else:
        desc = f"{bride_gana} and {groom_gana} — significant temperamental mismatch."

    return {
        "obtained": obtained,
        "max": 6,
        "bride_gana": bride_gana,
        "groom_gana": groom_gana,
        "description": desc,
    }


# ═══════════════════════════════════════════════════════════════════════════ #
# KOOTA 7: BHAKOOT — Emotional & Family Harmony (7 points)
# ═══════════════════════════════════════════════════════════════════════════ #

def calc_bhakoot_koota(bride_rashi_idx: int, groom_rashi_idx: int) -> dict:
    """
    Bhakoot Koota — emotional and family harmony between Moon signs.

    Dosha occurs when the relative Rashi positions form 2/12, 5/9, or 6/8.
    Dosha is cancelled when Rashi lords are the same or mutual friends.

    Parameters:
        bride_rashi_idx: Bride's Moon Rashi index (0-11)
        groom_rashi_idx: Groom's Moon Rashi index (0-11)

    Returns:
        dict with obtained, max, description, dosha_present, dosha_cancelled

    References:
        Muhurta Chintamani, Phaldeepika Ch. 7
    """
    # Relative positions (1-12)
    bride_to_groom: int = (groom_rashi_idx - bride_rashi_idx) % 12 + 1
    groom_to_bride: int = (bride_rashi_idx - groom_rashi_idx) % 12 + 1

    pair: tuple[int, int] = (bride_to_groom, groom_to_bride)
    has_dosha: bool = pair in BHAKOOT_DOSHA_PAIRS

    dosha_cancelled: bool = False
    if has_dosha:
        # Check cancellation: same lord or mutual friendship
        bride_lord: str = _get_rashi_lord(bride_rashi_idx)
        groom_lord: str = _get_rashi_lord(groom_rashi_idx)

        if bride_lord == groom_lord:
            dosha_cancelled = True
        else:
            f_bg: int = _get_graha_friendship(bride_lord, groom_lord)
            f_gb: int = _get_graha_friendship(groom_lord, bride_lord)
            if f_bg >= 1 and f_gb >= 1:
                dosha_cancelled = True

    if not has_dosha:
        obtained = np.float64(7.0)
        dosha_type = "None"
        desc = "No Bhakoot Dosha — excellent emotional and family harmony."
    elif dosha_cancelled:
        obtained = np.float64(7.0)
        dosha_type = f"{bride_to_groom}/{groom_to_bride} (Cancelled)"
        desc = (f"Bhakoot Dosha ({bride_to_groom}/{groom_to_bride}) present but cancelled — "
                f"Rashi lords are same or mutual friends.")
    else:
        obtained = np.float64(0.0)
        dosha_type = f"{bride_to_groom}/{groom_to_bride}"
        desc = f"Bhakoot Dosha ({bride_to_groom}/{groom_to_bride}) — emotional and family challenges indicated."

    return {
        "obtained": float(obtained),
        "max": 7,
        "positions": f"{bride_to_groom}/{groom_to_bride}",
        "dosha_present": has_dosha,
        "dosha_cancelled": dosha_cancelled,
        "dosha_type": dosha_type,
        "description": desc,
    }


# ═══════════════════════════════════════════════════════════════════════════ #
# KOOTA 8: NADI — Genetic & Health Compatibility (8 points)
# ═══════════════════════════════════════════════════════════════════════════ #

def calc_nadi_koota(
    bride_nak_idx: int, groom_nak_idx: int,
    bride_rashi_idx: int, groom_rashi_idx: int
) -> dict:
    """
    Nadi Koota — genetic and health compatibility.

    Same Nadi → Nadi Dosha (0 points). Different Nadi → 8 points.

    Cancellation conditions:
        1. Same Nakshatra but different Rashi → dosha cancelled.
        2. Same Rashi but different Nakshatra → dosha cancelled.

    Parameters:
        bride_nak_idx:   Bride's Nakshatra index (0-26)
        groom_nak_idx:   Groom's Nakshatra index (0-26)
        bride_rashi_idx: Bride's Moon Rashi index (0-11)
        groom_rashi_idx: Groom's Moon Rashi index (0-11)

    Returns:
        dict with obtained, max, bride_nadi, groom_nadi, description

    References:
        Brihat Parashara Hora Shastra, Ch. 79-80
    """
    bride_nadi: int = _get_nadi(bride_nak_idx)
    groom_nadi: int = _get_nadi(groom_nak_idx)
    bride_nadi_name: str = NADI_NAMES[bride_nadi]
    groom_nadi_name: str = NADI_NAMES[groom_nadi]

    same_nadi: bool = (bride_nadi == groom_nadi)
    dosha_cancelled: bool = False

    if same_nadi:
        # Check cancellation conditions
        same_nakshatra: bool = (bride_nak_idx == groom_nak_idx)
        same_rashi: bool = (bride_rashi_idx == groom_rashi_idx)
        different_rashi: bool = not same_rashi
        different_nakshatra: bool = not same_nakshatra

        if same_nakshatra and different_rashi:
            dosha_cancelled = True
        elif same_rashi and different_nakshatra:
            dosha_cancelled = True

    if not same_nadi:
        obtained = np.float64(8.0)
        desc = f"Different Nadis ({bride_nadi_name} and {groom_nadi_name}) — excellent health compatibility."
    elif dosha_cancelled:
        obtained = np.float64(8.0)
        desc = (f"Same Nadi ({bride_nadi_name}) but Nadi Dosha is cancelled — "
                f"acceptable health compatibility.")
    else:
        obtained = np.float64(0.0)
        desc = f"Same Nadi ({bride_nadi_name}) — Nadi Dosha present. Potential health/progeny concerns."

    return {
        "obtained": float(obtained),
        "max": 8,
        "bride_nadi": bride_nadi_name,
        "groom_nadi": groom_nadi_name,
        "dosha_present": same_nadi,
        "dosha_cancelled": dosha_cancelled,
        "description": desc,
    }


# ═══════════════════════════════════════════════════════════════════════════ #
# VEDHA CHECK — Nakshatra Repulsion
# ═══════════════════════════════════════════════════════════════════════════ #

def check_vedha(bride_nak_idx: int, groom_nak_idx: int) -> dict:
    """
    Check if the bride and groom Nakshatras form a Vedha (repulsion) pair.

    Vedha pairs are mutually afflicting Nakshatras that indicate obstacles
    and discord, regardless of the Koota score.

    Parameters:
        bride_nak_idx: Bride's Nakshatra index (0-26)
        groom_nak_idx: Groom's Nakshatra index (0-26)

    Returns:
        dict with has_vedha, description

    References:
        Muhurta Chintamani by Daivagna Rama
    """
    for a, b in VEDHA_PAIRS:
        if (bride_nak_idx == a and groom_nak_idx == b) or \
           (bride_nak_idx == b and groom_nak_idx == a):
            bride_name: str = NAKSHATRAS[bride_nak_idx]["name"]
            groom_name: str = NAKSHATRAS[groom_nak_idx]["name"]
            return {
                "has_vedha": True,
                "bride_nakshatra": bride_name,
                "groom_nakshatra": groom_name,
                "description": (
                    f"Vedha Dosha present — {bride_name} and {groom_name} are "
                    f"mutually afflicting Nakshatras. This is considered inauspicious."
                ),
            }

    return {
        "has_vedha": False,
        "description": "No Vedha Dosha — Nakshatras are not mutually afflicting.",
    }


# ═══════════════════════════════════════════════════════════════════════════ #
# MANGLIK DOSHA — Mars Placement Check
# ═══════════════════════════════════════════════════════════════════════════ #

def check_manglik_dosha(
    planets: dict,
    ascendant_sidereal: float
) -> dict:
    """
    Check if the native has Manglik (Kuja) Dosha.

    Manglik Dosha occurs when Mars is placed in houses 1, 2, 4, 7, 8, or 12
    from the Ascendant (Lagna).

    Cancellation conditions:
        1. Mars in its own sign (Aries or Scorpio)
        2. Mars is exalted (in Capricorn)
        3. Mars is debilitated (in Cancer) — some traditions consider this cancellation
        4. Jupiter or Venus aspects/conjoins Mars
        5. Both partners are Manglik (checked at the orchestration level)

    Parameters:
        planets: dict of planetary positions (from ephemeris)
        ascendant_sidereal: Sidereal ascendant longitude in degrees

    Returns:
        dict with is_manglik, mars_house, cancellation details

    References:
        Brihat Parashara Hora Shastra, Phaldeepika
    """
    mars_data = planets.get("Mars")
    if mars_data is None:
        return {
            "is_manglik": False,
            "description": "Mars data not available.",
        }

    mars_sid: float = mars_data.get("sidereal_longitude", 0.0)
    asc_sign_idx: int = int(np.float64(ascendant_sidereal) % np.float64(360.0) / np.float64(30.0))
    mars_sign_idx: int = int(np.float64(mars_sid) % np.float64(360.0) / np.float64(30.0))

    # Calculate Mars house from Lagna (whole sign system)
    mars_house: int = (mars_sign_idx - asc_sign_idx) % 12 + 1

    is_manglik: bool = mars_house in MANGLIK_HOUSES

    if not is_manglik:
        return {
            "is_manglik": False,
            "mars_house": mars_house,
            "description": f"Mars in house {mars_house} — no Manglik Dosha.",
        }

    # Check cancellation conditions
    cancellations: list[str] = []
    is_cancelled: bool = False

    mars_dignity = get_planetary_dignity("Mars", mars_sid)

    # Mars in own sign (Aries=0, Scorpio=7)
    if mars_sign_idx in [0, 7]:
        cancellations.append("Mars in own sign — Manglik Dosha cancelled.")
        is_cancelled = True

    # Mars exalted (Capricorn=9)
    if mars_sign_idx == 9:
        cancellations.append("Mars is exalted in Capricorn — Manglik Dosha cancelled.")
        is_cancelled = True

    # Jupiter or Venus in same house as Mars (conjunction check)
    for benefic in ["Jupiter", "Venus"]:
        if benefic in planets:
            benefic_sid: float = planets[benefic].get("sidereal_longitude", 0.0)
            benefic_sign: int = int(np.float64(benefic_sid) % np.float64(360.0) / np.float64(30.0))
            benefic_house: int = (benefic_sign - asc_sign_idx) % 12 + 1
            if benefic_house == mars_house:
                cancellations.append(
                    f"{benefic} conjoins Mars in house {mars_house} — Manglik Dosha mitigated."
                )
                is_cancelled = True

    if is_cancelled:
        desc = f"Mars in house {mars_house} — Manglik Dosha present but cancelled. " + \
               " ".join(cancellations)
    else:
        desc = (f"Mars in house {mars_house} — Manglik Dosha present. "
                f"May indicate challenges in marital harmony.")

    return {
        "is_manglik": True,
        "is_cancelled": is_cancelled,
        "mars_house": mars_house,
        "mars_sign": RASHIS[mars_sign_idx]["name"],
        "mars_dignity": mars_dignity.get("status", ""),
        "cancellations": cancellations,
        "description": desc,
    }


# ═══════════════════════════════════════════════════════════════════════════ #
# MASTER FUNCTION — Complete Kundali Matching
# ═══════════════════════════════════════════════════════════════════════════ #

def compute_kundali_matching(
    bride_moon_lon: float,
    groom_moon_lon: float,
    bride_planets: dict,
    groom_planets: dict,
    bride_asc_sid: float,
    groom_asc_sid: float,
) -> dict:
    """
    Compute complete Kundali Matching: Ashta Koota Milan (36 points)
    + Vedha check + Manglik Dosha for both partners.

    This is the master orchestration function that calls all individual
    Koota computations, aggregates scores, and generates a final verdict.

    Parameters:
        bride_moon_lon:  Bride's Moon sidereal longitude (degrees, float64)
        groom_moon_lon:  Groom's Moon sidereal longitude (degrees, float64)
        bride_planets:   Bride's planetary positions dict
        groom_planets:   Groom's planetary positions dict
        bride_asc_sid:   Bride's sidereal ascendant longitude (degrees)
        groom_asc_sid:   Groom's sidereal ascendant longitude (degrees)

    Returns:
        Comprehensive matching result dict with 8 Koota scores, total,
        Vedha status, Manglik Dosha for both, and interpretation.

    References:
        Brihat Parashara Hora Shastra Ch. 79-80
        Muhurta Chintamani by Daivagna Rama
    """
    # Determine Nakshatra and Rashi for both
    bride_nak = get_nakshatra(bride_moon_lon)
    groom_nak = get_nakshatra(groom_moon_lon)
    bride_rashi = get_rashi(bride_moon_lon)
    groom_rashi = get_rashi(groom_moon_lon)

    # 0-based indices
    b_nak_idx: int = bride_nak["index"] - 1   # NAKSHATRAS uses 1-based index
    g_nak_idx: int = groom_nak["index"] - 1
    b_rashi_idx: int = bride_rashi["index"] - 1  # RASHIS uses 1-based index
    g_rashi_idx: int = groom_rashi["index"] - 1

    # ── Compute all 8 Kootas ──
    varna = calc_varna_koota(b_rashi_idx, g_rashi_idx)
    vashya = calc_vashya_koota(b_rashi_idx, g_rashi_idx)
    tara = calc_tara_koota(b_nak_idx, g_nak_idx)
    yoni = calc_yoni_koota(b_nak_idx, g_nak_idx)
    graha_maitri = calc_graha_maitri_koota(b_rashi_idx, g_rashi_idx)
    gana = calc_gana_koota(b_nak_idx, g_nak_idx)
    bhakoot = calc_bhakoot_koota(b_rashi_idx, g_rashi_idx)
    nadi = calc_nadi_koota(b_nak_idx, g_nak_idx, b_rashi_idx, g_rashi_idx)

    # ── Total Score ──
    total_points: float = (
        varna["obtained"] + vashya["obtained"] + tara["obtained"] +
        yoni["obtained"] + graha_maitri["obtained"] + gana["obtained"] +
        bhakoot["obtained"] + nadi["obtained"]
    )
    max_points: int = 36

    # ── Compatibility Level ──
    if total_points >= 32:
        level = "Excellent"
        level_desc = ("Exceptionally high compatibility. "
                      "The union is expected to be deeply harmonious.")
    elif total_points >= 24:
        level = "Very Good"
        level_desc = ("Strong compatibility across most factors. "
                      "A very favourable match.")
    elif total_points >= 18:
        level = "Acceptable"
        level_desc = ("Adequate compatibility for marriage. "
                      "Minor differences may exist but can be managed.")
    elif total_points >= 12:
        level = "Below Average"
        level_desc = ("Compatibility is below the traditional threshold. "
                      "Careful consideration recommended.")
    else:
        level = "Poor"
        level_desc = ("Low compatibility. Traditional Jyotisha would "
                      "advise caution or remedies before proceeding.")

    # ── Vedha Check ──
    vedha = check_vedha(b_nak_idx, g_nak_idx)

    # ── Manglik Dosha ──
    bride_manglik = check_manglik_dosha(bride_planets, bride_asc_sid)
    groom_manglik = check_manglik_dosha(groom_planets, groom_asc_sid)

    # Double-Manglik cancellation: if both are Manglik, neutralized
    both_manglik: bool = (
        bride_manglik.get("is_manglik", False) and
        groom_manglik.get("is_manglik", False)
    )
    if both_manglik:
        bride_manglik["double_manglik_cancellation"] = True
        groom_manglik["double_manglik_cancellation"] = True

    # ── Generate conclusion ──
    warnings: list[str] = []
    if total_points < 18:
        warnings.append(f"Total score ({total_points}/36) is below the traditional threshold of 18.")
    if vedha.get("has_vedha"):
        warnings.append("Vedha Dosha is present — Nakshatras are mutually afflicting.")
    if bride_manglik.get("is_manglik") and not bride_manglik.get("is_cancelled") and not both_manglik:
        warnings.append("Bride has uncancelled Manglik Dosha.")
    if groom_manglik.get("is_manglik") and not groom_manglik.get("is_cancelled") and not both_manglik:
        warnings.append("Groom has uncancelled Manglik Dosha.")
    if nadi.get("dosha_present") and not nadi.get("dosha_cancelled"):
        warnings.append("Nadi Dosha is present — health/progeny concerns indicated.")
    if bhakoot.get("dosha_present") and not bhakoot.get("dosha_cancelled"):
        warnings.append("Bhakoot Dosha is present — emotional/family challenges indicated.")

    if not warnings:
        conclusion = f"Match score: {total_points}/{max_points} ({level}). {level_desc} No major doshas detected."
    else:
        conclusion = (
            f"Match score: {total_points}/{max_points} ({level}). {level_desc} "
            f"Warnings: {'; '.join(warnings)}"
        )

    return {
        "bride": {
            "nakshatra": bride_nak,
            "rashi": bride_rashi,
            "moon_longitude": float(bride_moon_lon),
        },
        "groom": {
            "nakshatra": groom_nak,
            "rashi": groom_rashi,
            "moon_longitude": float(groom_moon_lon),
        },
        "kootas": {
            "varna": varna,
            "vashya": vashya,
            "tara": tara,
            "yoni": yoni,
            "graha_maitri": graha_maitri,
            "gana": gana,
            "bhakoot": bhakoot,
            "nadi": nadi,
        },
        "total_points": total_points,
        "max_points": max_points,
        "compatibility_level": level,
        "compatibility_description": level_desc,
        "vedha": vedha,
        "manglik_dosha": {
            "bride": bride_manglik,
            "groom": groom_manglik,
            "both_manglik_cancellation": both_manglik,
        },
        "warnings": warnings,
        "conclusion": conclusion,
    }
