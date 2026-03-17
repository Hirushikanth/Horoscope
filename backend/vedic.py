"""
vedic.py — Vedic Astrology Calculation Module
================================================
Implements traditional Jyotisha algorithms: Nakshatras, Rashis, Bhavas,
Vimshottari Dasha, Panchang, divisional charts, Yogas, planetary dignity.
All computations in IEEE 754 float64 precision.

References:
- Brihat Parashara Hora Shastra
- Saravali by Kalyana Varma
- Phaldeepika by Mantreswara
"""

import numpy as np
from datetime import datetime, timedelta

# ═══════════════════════════════════════════════════════════════════════════ #
# 27 NAKSHATRAS — Each spans 13°20' (13.333...°)
# ═══════════════════════════════════════════════════════════════════════════ #

NAKSHATRA_SPAN = np.float64(360.0) / np.float64(27.0)  # 13.33333...°

NAKSHATRAS = [
    {"index": 1,  "name": "Ashwini",           "sanskrit": "अश्विनी",      "ruler": "Ketu",    "deity": "Ashwini Kumaras", "gana": "Deva",    "animal": "Horse",    "guna": "Rajas"},
    {"index": 2,  "name": "Bharani",            "sanskrit": "भरणी",         "ruler": "Venus",   "deity": "Yama",            "gana": "Manushya","animal": "Elephant", "guna": "Rajas"},
    {"index": 3,  "name": "Krittika",           "sanskrit": "कृत्तिका",     "ruler": "Sun",     "deity": "Agni",            "gana": "Rakshasa","animal": "Goat",     "guna": "Rajas"},
    {"index": 4,  "name": "Rohini",             "sanskrit": "रोहिणी",       "ruler": "Moon",    "deity": "Brahma",          "gana": "Manushya","animal": "Serpent",  "guna": "Rajas"},
    {"index": 5,  "name": "Mrigashira",         "sanskrit": "मृगशिरा",      "ruler": "Mars",    "deity": "Soma",            "gana": "Deva",    "animal": "Serpent",  "guna": "Tamas"},
    {"index": 6,  "name": "Ardra",              "sanskrit": "आर्द्रा",       "ruler": "Rahu",    "deity": "Rudra",           "gana": "Manushya","animal": "Dog",      "guna": "Tamas"},
    {"index": 7,  "name": "Punarvasu",          "sanskrit": "पुनर्वसु",     "ruler": "Jupiter", "deity": "Aditi",            "gana": "Deva",    "animal": "Cat",      "guna": "Tamas"},
    {"index": 8,  "name": "Pushya",             "sanskrit": "पुष्य",        "ruler": "Saturn",  "deity": "Brihaspati",      "gana": "Deva",    "animal": "Goat",     "guna": "Sattva"},
    {"index": 9,  "name": "Ashlesha",           "sanskrit": "आश्लेषा",      "ruler": "Mercury", "deity": "Sarpa",            "gana": "Rakshasa","animal": "Cat",      "guna": "Sattva"},
    {"index": 10, "name": "Magha",              "sanskrit": "मघा",          "ruler": "Ketu",    "deity": "Pitris",           "gana": "Rakshasa","animal": "Rat",      "guna": "Sattva"},
    {"index": 11, "name": "Purva Phalguni",     "sanskrit": "पूर्व फाल्गुनी","ruler": "Venus",   "deity": "Bhaga",            "gana": "Manushya","animal": "Rat",      "guna": "Rajas"},
    {"index": 12, "name": "Uttara Phalguni",    "sanskrit": "उत्तर फाल्गुनी","ruler": "Sun",     "deity": "Aryaman",          "gana": "Manushya","animal": "Cow",      "guna": "Rajas"},
    {"index": 13, "name": "Hasta",              "sanskrit": "हस्त",         "ruler": "Moon",    "deity": "Savitar",          "gana": "Deva",    "animal": "Buffalo",  "guna": "Rajas"},
    {"index": 14, "name": "Chitra",             "sanskrit": "चित्रा",       "ruler": "Mars",    "deity": "Vishvakarma",      "gana": "Rakshasa","animal": "Tiger",    "guna": "Tamas"},
    {"index": 15, "name": "Swati",              "sanskrit": "स्वाती",       "ruler": "Rahu",    "deity": "Vayu",             "gana": "Deva",    "animal": "Buffalo",  "guna": "Tamas"},
    {"index": 16, "name": "Vishakha",           "sanskrit": "विशाखा",       "ruler": "Jupiter", "deity": "Indra-Agni",       "gana": "Rakshasa","animal": "Tiger",    "guna": "Tamas"},
    {"index": 17, "name": "Anuradha",           "sanskrit": "अनुराधा",      "ruler": "Saturn",  "deity": "Mitra",            "gana": "Deva",    "animal": "Deer",     "guna": "Sattva"},
    {"index": 18, "name": "Jyeshtha",           "sanskrit": "ज्येष्ठा",     "ruler": "Mercury", "deity": "Indra",            "gana": "Rakshasa","animal": "Deer",     "guna": "Sattva"},
    {"index": 19, "name": "Moola",              "sanskrit": "मूल",          "ruler": "Ketu",    "deity": "Nirriti",          "gana": "Rakshasa","animal": "Dog",      "guna": "Sattva"},
    {"index": 20, "name": "Purva Ashadha",      "sanskrit": "पूर्वाषाढा",   "ruler": "Venus",   "deity": "Apas",             "gana": "Manushya","animal": "Monkey",   "guna": "Rajas"},
    {"index": 21, "name": "Uttara Ashadha",     "sanskrit": "उत्तराषाढा",   "ruler": "Sun",     "deity": "Vishve Devas",     "gana": "Manushya","animal": "Mongoose", "guna": "Rajas"},
    {"index": 22, "name": "Shravana",           "sanskrit": "श्रवण",        "ruler": "Moon",    "deity": "Vishnu",           "gana": "Deva",    "animal": "Monkey",   "guna": "Rajas"},
    {"index": 23, "name": "Dhanishta",          "sanskrit": "धनिष्ठा",      "ruler": "Mars",    "deity": "Vasus",            "gana": "Rakshasa","animal": "Lion",     "guna": "Tamas"},
    {"index": 24, "name": "Shatabhisha",        "sanskrit": "शतभिषा",       "ruler": "Rahu",    "deity": "Varuna",           "gana": "Rakshasa","animal": "Horse",    "guna": "Tamas"},
    {"index": 25, "name": "Purva Bhadrapada",   "sanskrit": "पूर्वभाद्रपदा","ruler": "Jupiter", "deity": "Aja Ekapada",      "gana": "Manushya","animal": "Lion",     "guna": "Tamas"},
    {"index": 26, "name": "Uttara Bhadrapada",  "sanskrit": "उत्तरभाद्रपदा","ruler": "Saturn",  "deity": "Ahir Budhnya",     "gana": "Manushya","animal": "Cow",      "guna": "Sattva"},
    {"index": 27, "name": "Revati",             "sanskrit": "रेवती",        "ruler": "Mercury", "deity": "Pushan",           "gana": "Deva",    "animal": "Elephant", "guna": "Sattva"},
]

# ═══════════════════════════════════════════════════════════════════════════ #
# 12 RASHIS (Zodiac Signs) — Each spans 30°
# ═══════════════════════════════════════════════════════════════════════════ #

RASHIS = [
    {"index": 1,  "name": "Mesha",    "english": "Aries",       "lord": "Mars",    "element": "Fire",  "quality": "Movable",  "symbol": "♈"},
    {"index": 2,  "name": "Vrishabha","english": "Taurus",      "lord": "Venus",   "element": "Earth", "quality": "Fixed",    "symbol": "♉"},
    {"index": 3,  "name": "Mithuna",  "english": "Gemini",      "lord": "Mercury", "element": "Air",   "quality": "Dual",     "symbol": "♊"},
    {"index": 4,  "name": "Karka",    "english": "Cancer",      "lord": "Moon",    "element": "Water", "quality": "Movable",  "symbol": "♋"},
    {"index": 5,  "name": "Simha",    "english": "Leo",         "lord": "Sun",     "element": "Fire",  "quality": "Fixed",    "symbol": "♌"},
    {"index": 6,  "name": "Kanya",    "english": "Virgo",       "lord": "Mercury", "element": "Earth", "quality": "Dual",     "symbol": "♍"},
    {"index": 7,  "name": "Tula",     "english": "Libra",       "lord": "Venus",   "element": "Air",   "quality": "Movable",  "symbol": "♎"},
    {"index": 8,  "name": "Vrischika","english": "Scorpio",     "lord": "Mars",    "element": "Water", "quality": "Fixed",    "symbol": "♏"},
    {"index": 9,  "name": "Dhanu",    "english": "Sagittarius", "lord": "Jupiter", "element": "Fire",  "quality": "Dual",     "symbol": "♐"},
    {"index": 10, "name": "Makara",   "english": "Capricorn",   "lord": "Saturn",  "element": "Earth", "quality": "Movable",  "symbol": "♑"},
    {"index": 11, "name": "Kumbha",   "english": "Aquarius",    "lord": "Saturn",  "element": "Air",   "quality": "Fixed",    "symbol": "♒"},
    {"index": 12, "name": "Meena",    "english": "Pisces",      "lord": "Jupiter", "element": "Water", "quality": "Dual",     "symbol": "♓"},
]

# ═══════════════════════════════════════════════════════════════════════════ #
# 12 BHAVAS (Houses) — Significations
# ═══════════════════════════════════════════════════════════════════════════ #

BHAVA_SIGNIFICATIONS = {
    1:  {"name": "Tanu Bhava",    "keywords": "Self, personality, physique, health, vitality"},
    2:  {"name": "Dhana Bhava",   "keywords": "Wealth, family, speech, food, values"},
    3:  {"name": "Sahaja Bhava",  "keywords": "Siblings, courage, communication, short journeys"},
    4:  {"name": "Sukha Bhava",   "keywords": "Mother, home, comfort, vehicles, education"},
    5:  {"name": "Putra Bhava",   "keywords": "Children, intelligence, creativity, romance, past merit"},
    6:  {"name": "Shatru Bhava",  "keywords": "Enemies, disease, debt, service, competition"},
    7:  {"name": "Kalatra Bhava", "keywords": "Spouse, marriage, partnerships, business"},
    8:  {"name": "Ayu Bhava",     "keywords": "Longevity, transformation, occult, inheritance"},
    9:  {"name": "Dharma Bhava",  "keywords": "Father, luck, dharma, higher learning, pilgrimages"},
    10: {"name": "Karma Bhava",   "keywords": "Career, status, authority, public life"},
    11: {"name": "Labha Bhava",   "keywords": "Gains, income, friends, aspirations, elder siblings"},
    12: {"name": "Vyaya Bhava",   "keywords": "Losses, expenses, liberation, foreign lands, isolation"},
}

# ═══════════════════════════════════════════════════════════════════════════ #
# VIMSHOTTARI DASHA — 120-year cycle
# ═══════════════════════════════════════════════════════════════════════════ #

DASHA_SEQUENCE = ['Ketu', 'Venus', 'Sun', 'Moon', 'Mars', 'Rahu', 'Jupiter', 'Saturn', 'Mercury']
DASHA_YEARS = {
    'Ketu': np.float64(7.0), 'Venus': np.float64(20.0), 'Sun': np.float64(6.0),
    'Moon': np.float64(10.0), 'Mars': np.float64(7.0), 'Rahu': np.float64(18.0),
    'Jupiter': np.float64(16.0), 'Saturn': np.float64(19.0), 'Mercury': np.float64(17.0),
}
TOTAL_DASHA_YEARS = np.float64(120.0)

# Nakshatra → starting Dasha lord mapping
NAKSHATRA_DASHA_LORD = [
    'Ketu', 'Venus', 'Sun', 'Moon', 'Mars', 'Rahu', 'Jupiter', 'Saturn', 'Mercury',
    'Ketu', 'Venus', 'Sun', 'Moon', 'Mars', 'Rahu', 'Jupiter', 'Saturn', 'Mercury',
    'Ketu', 'Venus', 'Sun', 'Moon', 'Mars', 'Rahu', 'Jupiter', 'Saturn', 'Mercury',
]

# ═══════════════════════════════════════════════════════════════════════════ #
# PLANETARY DIGNITY — Exaltation, Debilitation, Own Sign, Moolatrikona
# ═══════════════════════════════════════════════════════════════════════════ #

EXALTATION = {'Sun': (1, 10.0), 'Moon': (2, 3.0), 'Mars': (10, 28.0), 'Mercury': (6, 15.0),
              'Jupiter': (4, 5.0), 'Venus': (12, 27.0), 'Saturn': (7, 20.0)}
DEBILITATION = {'Sun': (7, 10.0), 'Moon': (8, 3.0), 'Mars': (4, 28.0), 'Mercury': (12, 15.0),
                'Jupiter': (10, 5.0), 'Venus': (6, 27.0), 'Saturn': (1, 20.0)}
OWN_SIGNS = {'Sun': [5], 'Moon': [4], 'Mars': [1, 8], 'Mercury': [3, 6],
             'Jupiter': [9, 12], 'Venus': [2, 7], 'Saturn': [10, 11]}
MOOLATRIKONA = {'Sun': (5, 0, 20), 'Moon': (2, 3, 30), 'Mars': (1, 0, 12),
                'Mercury': (6, 15, 20), 'Jupiter': (9, 0, 10), 'Venus': (7, 0, 15),
                'Saturn': (11, 0, 20)}


# ═══════════════════════════════════════════════════════════════════════════ #
# FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════ #

def get_nakshatra(sidereal_lon: float) -> dict:
    """Determine the Nakshatra, pada, and ruling planet for a sidereal longitude."""
    lon = np.float64(sidereal_lon) % np.float64(360.0)
    nak_index = int(lon / NAKSHATRA_SPAN)  # 0-26
    deg_in_nak = lon - np.float64(nak_index) * NAKSHATRA_SPAN
    pada = int(deg_in_nak / (NAKSHATRA_SPAN / np.float64(4.0))) + 1
    if pada > 4:
        pada = 4
    nak = NAKSHATRAS[nak_index]
    return {
        **nak,
        'pada': pada,
        'degree_in_nakshatra': float(deg_in_nak),
        'total_degree': float(lon),
        'percentage_traversed': float(deg_in_nak / NAKSHATRA_SPAN * np.float64(100.0)),
    }


def get_rashi(sidereal_lon: float) -> dict:
    """Determine the Rashi (zodiac sign) for a sidereal longitude."""
    lon = np.float64(sidereal_lon) % np.float64(360.0)
    rashi_index = int(lon / np.float64(30.0))  # 0-11
    deg_in_sign = float(lon - np.float64(rashi_index) * np.float64(30.0))
    rashi = RASHIS[rashi_index]
    return {**rashi, 'degree_in_sign': deg_in_sign}


def get_bhava(planets: dict, ascendant_sidereal: float) -> list:
    """
    Calculate 12 Bhavas (Houses) using Whole Sign house system.
    House 1 = sign of the Ascendant. Each subsequent sign = next house.
    """
    asc_lon = np.float64(ascendant_sidereal) % np.float64(360.0)
    asc_sign_index = int(asc_lon / np.float64(30.0))  # 0-11

    bhavas = []
    for i in range(12):
        house_num = i + 1
        sign_index = (asc_sign_index + i) % 12
        rashi = RASHIS[sign_index]
        sig = BHAVA_SIGNIFICATIONS[house_num]

        occupants = []
        for pname, pdata in planets.items():
            if pname.startswith('_'):
                continue
            p_lon = np.float64(pdata.get('sidereal_longitude', 0))
            p_sign = int(p_lon / np.float64(30.0))
            if p_sign == sign_index:
                occupants.append(pname)

        bhavas.append({
            'house': house_num,
            'sign': rashi['name'],
            'sign_english': rashi['english'],
            'sign_symbol': rashi['symbol'],
            'lord': rashi['lord'],
            'signification': sig['name'],
            'keywords': sig['keywords'],
            'occupants': occupants,
        })
    return bhavas


def get_janma_nakshatra(moon_sidereal_lon: float) -> dict:
    """Get comprehensive Janma (birth) Nakshatra details from Moon's sidereal longitude."""
    nak = get_nakshatra(moon_sidereal_lon)
    rashi = get_rashi(moon_sidereal_lon)
    dasha_lord = NAKSHATRA_DASHA_LORD[nak['index'] - 1]
    dasha_balance = _compute_dasha_balance(nak)
    return {
        **nak,
        'moon_rashi': rashi,
        'dasha_lord_at_birth': dasha_lord,
        'dasha_balance_years': dasha_balance,
        'moon_longitude': float(moon_sidereal_lon),
    }


def _compute_dasha_balance(nakshatra_info: dict) -> float:
    """Compute remaining Dasha balance at birth based on Moon's position in Nakshatra."""
    fraction_remaining = np.float64(1.0) - np.float64(nakshatra_info['percentage_traversed']) / np.float64(100.0)
    lord = NAKSHATRA_DASHA_LORD[nakshatra_info['index'] - 1]
    total_years = DASHA_YEARS[lord]
    return float(fraction_remaining * total_years)


# ═══════════════════════════════════════════════════════════════════════════ #
# VIMSHOTTARI DASHA TIMELINE
# ═══════════════════════════════════════════════════════════════════════════ #

def get_vimshottari_dasha(moon_sidereal_lon: float, birth_date_str: str) -> dict:
    """
    Calculate complete Vimshottari Dasha timeline:
    Mahadasha → Antardasha → Pratyantardasha.
    """
    nak = get_nakshatra(moon_sidereal_lon)
    start_lord_idx = DASHA_SEQUENCE.index(NAKSHATRA_DASHA_LORD[nak['index'] - 1])
    balance = _compute_dasha_balance(nak)

    parts = birth_date_str.split('-')
    birth_dt = datetime(int(parts[0]), int(parts[1]), int(parts[2]))

    mahadashas = []
    current_dt = birth_dt

    for cycle in range(2):  # 2 full cycles = 240 years coverage
        for i in range(9):
            lord_idx = (start_lord_idx + i) % 9
            lord = DASHA_SEQUENCE[lord_idx]
            total_years = DASHA_YEARS[lord]

            if cycle == 0 and i == 0:
                years = np.float64(balance)
            else:
                years = total_years

            days = years * np.float64(365.25)
            end_dt = current_dt + timedelta(days=float(days))

            antardashas = _calculate_antardashas(lord, lord_idx, current_dt, end_dt, years)

            mahadashas.append({
                'lord': lord,
                'total_years': float(total_years),
                'effective_years': float(years),
                'start_date': current_dt.strftime('%Y-%m-%d'),
                'end_date': end_dt.strftime('%Y-%m-%d'),
                'antardashas': antardashas,
            })
            current_dt = end_dt

    return {
        'birth_nakshatra': nak['name'],
        'dasha_lord_at_birth': NAKSHATRA_DASHA_LORD[nak['index'] - 1],
        'balance_years': float(balance),
        'mahadashas': mahadashas,
    }


def _calculate_antardashas(maha_lord, maha_lord_idx, maha_start, maha_end, maha_years):
    """Calculate Antardasha sub-periods within a Mahadasha."""
    antardashas = []
    current = maha_start
    for i in range(9):
        lord_idx = (maha_lord_idx + i) % 9
        ad_lord = DASHA_SEQUENCE[lord_idx]
        ad_years = maha_years * DASHA_YEARS[ad_lord] / TOTAL_DASHA_YEARS
        ad_days = ad_years * np.float64(365.25)
        ad_end = current + timedelta(days=float(ad_days))

        pratyantar = _calculate_pratyantardashas(lord_idx, current, ad_end, ad_years)

        antardashas.append({
            'lord': ad_lord,
            'years': float(ad_years),
            'start_date': current.strftime('%Y-%m-%d'),
            'end_date': ad_end.strftime('%Y-%m-%d'),
            'pratyantardashas': pratyantar,
        })
        current = ad_end
    return antardashas


def _calculate_pratyantardashas(ad_lord_idx, ad_start, ad_end, ad_years):
    """Calculate Pratyantardasha sub-sub-periods."""
    pratyantars = []
    current = ad_start
    for i in range(9):
        lord_idx = (ad_lord_idx + i) % 9
        pd_lord = DASHA_SEQUENCE[lord_idx]
        pd_years = ad_years * DASHA_YEARS[pd_lord] / TOTAL_DASHA_YEARS
        pd_days = pd_years * np.float64(365.25)
        pd_end = current + timedelta(days=float(pd_days))

        pratyantars.append({
            'lord': pd_lord,
            'years': float(pd_years),
            'start_date': current.strftime('%Y-%m-%d'),
            'end_date': pd_end.strftime('%Y-%m-%d'),
        })
        current = pd_end
    return pratyantars


# ═══════════════════════════════════════════════════════════════════════════ #
# PANCHANG — Five Elements of Hindu Calendar
# ═══════════════════════════════════════════════════════════════════════════ #

TITHI_NAMES = [
    "Pratipada", "Dwitiya", "Tritiya", "Chaturthi", "Panchami",
    "Shashthi", "Saptami", "Ashtami", "Navami", "Dashami",
    "Ekadashi", "Dwadashi", "Trayodashi", "Chaturdashi", "Purnima",
    "Pratipada", "Dwitiya", "Tritiya", "Chaturthi", "Panchami",
    "Shashthi", "Saptami", "Ashtami", "Navami", "Dashami",
    "Ekadashi", "Dwadashi", "Trayodashi", "Chaturdashi", "Amavasya",
]

VARA_NAMES = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
VARA_SANSKRIT = ["Ravivara", "Somavara", "Mangalavara", "Budhavara", "Guruvara", "Shukravara", "Shanivara"]
VARA_LORDS = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]

YOGA_NAMES = [
    "Vishkambha", "Priti", "Ayushman", "Saubhagya", "Shobhana",
    "Atiganda", "Sukarma", "Dhriti", "Shoola", "Ganda",
    "Vriddhi", "Dhruva", "Vyaghata", "Harshana", "Vajra",
    "Siddhi", "Vyatipata", "Variyan", "Parigha", "Shiva",
    "Siddha", "Sadhya", "Shubha", "Shukla", "Brahma",
    "Indra", "Vaidhriti",
]

KARANA_NAMES = [
    "Bava", "Balava", "Kaulava", "Taitila", "Garija", "Vanija", "Vishti",
    "Shakuni", "Chatushpada", "Naga", "Kimstughna",
]


def get_panchang(sun_sidereal_lon: float, moon_sidereal_lon: float, weekday: int) -> dict:
    """
    Calculate Panchang: Tithi, Vara, Nakshatra, Yoga, Karana.

    Tithi: Angular difference Moon - Sun, each 12° = 1 Tithi (30 total)
    Yoga: Sum of Moon + Sun longitudes, each 13°20' = 1 Yoga (27 total)
    Karana: Half-tithi (60 total in a lunar month)
    """
    sun_lon = np.float64(sun_sidereal_lon)
    moon_lon = np.float64(moon_sidereal_lon)

    # Tithi: (Moon - Sun) / 12°
    diff = (moon_lon - sun_lon) % np.float64(360.0)
    tithi_index = int(diff / np.float64(12.0))
    tithi_remaining = float((np.float64(tithi_index + 1) * np.float64(12.0) - diff) / np.float64(12.0) * np.float64(100.0))

    paksha = "Shukla" if tithi_index < 15 else "Krishna"
    tithi_name = TITHI_NAMES[tithi_index]

    # Vara
    vara = VARA_NAMES[weekday]
    vara_sanskrit = VARA_SANSKRIT[weekday]
    vara_lord = VARA_LORDS[weekday]

    # Nakshatra (of Moon)
    moon_nak = get_nakshatra(moon_sidereal_lon)

    # Yoga: (Sun + Moon) / 13°20'
    yoga_sum = (sun_lon + moon_lon) % np.float64(360.0)
    yoga_index = int(yoga_sum / NAKSHATRA_SPAN)
    if yoga_index >= 27:
        yoga_index = 26

    # Karana: half-tithi
    karana_index_raw = int(diff / np.float64(6.0))
    if karana_index_raw == 0:
        karana_name = KARANA_NAMES[10]  # Kimstughna
    elif karana_index_raw >= 57:
        fixed_idx = karana_index_raw - 57
        karana_name = KARANA_NAMES[7 + fixed_idx] if fixed_idx < 4 else KARANA_NAMES[7]
    else:
        karana_name = KARANA_NAMES[(karana_index_raw - 1) % 7]

    return {
        'tithi': {
            'name': tithi_name,
            'number': tithi_index + 1,
            'paksha': paksha,
            'remaining_percentage': tithi_remaining,
        },
        'vara': {
            'name': vara,
            'sanskrit': vara_sanskrit,
            'lord': vara_lord,
        },
        'nakshatra': moon_nak,
        'yoga': {
            'name': YOGA_NAMES[yoga_index],
            'number': yoga_index + 1,
        },
        'karana': {
            'name': karana_name,
        },
    }


# ═══════════════════════════════════════════════════════════════════════════ #
# DIVISIONAL CHARTS — D-9 (Navamsa) and D-10 (Dasamsa)
# ═══════════════════════════════════════════════════════════════════════════ #

def get_navamsa(sidereal_lon: float) -> dict:
    """
    D-9 Navamsa chart position.
    Each sign (30°) is divided into 9 parts of 3°20' each.
    The navamsa sign is determined by the sequence starting from the element of the rashi.
    """
    lon = np.float64(sidereal_lon) % np.float64(360.0)
    sign_index = int(lon / np.float64(30.0))  # 0-11
    deg_in_sign = lon - np.float64(sign_index) * np.float64(30.0)
    navamsa_part = int(deg_in_sign / (np.float64(30.0) / np.float64(9.0)))  # 0-8
    if navamsa_part > 8:
        navamsa_part = 8

    # Starting sign for navamsa based on element
    element_start = [0, 9, 6, 3]  # Fire=Aries, Earth=Cap, Air=Libra, Water=Cancer
    element_idx = sign_index % 4
    navamsa_sign_index = (element_start[element_idx] + navamsa_part) % 12

    return {
        **RASHIS[navamsa_sign_index],
        'navamsa_part': navamsa_part + 1,
        'original_sign': RASHIS[sign_index]['name'],
    }


def get_dasamsa(sidereal_lon: float) -> dict:
    """
    D-10 Dasamsa chart position.
    Each sign (30°) divided into 10 parts of 3° each.
    Odd signs start from same sign, even signs start from 9th sign.
    """
    lon = np.float64(sidereal_lon) % np.float64(360.0)
    sign_index = int(lon / np.float64(30.0))
    deg_in_sign = lon - np.float64(sign_index) * np.float64(30.0)
    dasamsa_part = int(deg_in_sign / np.float64(3.0))
    if dasamsa_part > 9:
        dasamsa_part = 9

    if (sign_index + 1) % 2 == 1:  # Odd sign
        d10_sign = (sign_index + dasamsa_part) % 12
    else:  # Even sign
        d10_sign = (sign_index + 8 + dasamsa_part) % 12

    return {
        **RASHIS[d10_sign],
        'dasamsa_part': dasamsa_part + 1,
        'original_sign': RASHIS[sign_index]['name'],
    }


def get_divisional_charts(planets: dict) -> dict:
    """Compute D-1, D-9, D-10 for all planets."""
    d1 = {}
    d9 = {}
    d10 = {}
    for name, data in planets.items():
        if name.startswith('_'):
            continue
        sid_lon = data.get('sidereal_longitude', 0)
        d1[name] = get_rashi(sid_lon)
        d9[name] = get_navamsa(sid_lon)
        d10[name] = get_dasamsa(sid_lon)
    return {'D1_Rasi': d1, 'D9_Navamsa': d9, 'D10_Dasamsa': d10}


# ═══════════════════════════════════════════════════════════════════════════ #
# YOGA DETECTION
# ═══════════════════════════════════════════════════════════════════════════ #

def detect_yogas(planets: dict, bhavas: list) -> list:
    """Detect common astrological Yogas from planetary positions and house placements."""
    yogas = []
    planet_houses = {}
    for bhava in bhavas:
        for occ in bhava['occupants']:
            planet_houses[occ] = bhava['house']

    # Gajakesari Yoga: Jupiter in kendra (1,4,7,10) from Moon
    moon_house = planet_houses.get('Moon')
    jup_house = planet_houses.get('Jupiter')
    if moon_house and jup_house:
        diff = ((jup_house - moon_house) % 12)
        if diff in [0, 3, 6, 9]:
            yogas.append({
                'name': 'Gajakesari Yoga',
                'description': 'Jupiter in a Kendra from Moon — brings wisdom, wealth, and respect.',
                'planets': ['Jupiter', 'Moon'],
                'type': 'Benefic',
            })

    # Budhaditya Yoga: Sun + Mercury in same house
    if planet_houses.get('Sun') and planet_houses.get('Mercury'):
        if planet_houses['Sun'] == planet_houses['Mercury']:
            yogas.append({
                'name': 'Budhaditya Yoga',
                'description': 'Sun and Mercury conjunct — sharp intellect and communication skills.',
                'planets': ['Sun', 'Mercury'],
                'type': 'Benefic',
            })

    # Chandra-Mangal Yoga: Moon + Mars in same house
    if planet_houses.get('Moon') and planet_houses.get('Mars'):
        if planet_houses['Moon'] == planet_houses['Mars']:
            yogas.append({
                'name': 'Chandra-Mangal Yoga',
                'description': 'Moon and Mars conjunct — financial prosperity through determination.',
                'planets': ['Moon', 'Mars'],
                'type': 'Benefic',
            })

    # Raj Yoga: Lords of Kendra (1,4,7,10) and Trikona (1,5,9) conjunct
    kendra_lords = set()
    trikona_lords = set()
    for bhava in bhavas:
        if bhava['house'] in [1, 4, 7, 10]:
            kendra_lords.add(bhava['lord'])
        if bhava['house'] in [1, 5, 9]:
            trikona_lords.add(bhava['lord'])
    raj_lords = kendra_lords & trikona_lords
    for lord in raj_lords:
        if lord in planet_houses:
            yogas.append({
                'name': 'Raj Yoga',
                'description': f'{lord} is lord of both Kendra and Trikona — power, authority, and success.',
                'planets': [lord],
                'type': 'Benefic',
            })

    # Kemadruma Yoga: No planets in 2nd or 12th from Moon
    if moon_house:
        h2 = ((moon_house) % 12) + 1
        h12 = ((moon_house - 2) % 12) + 1
        planets_near_moon = []
        for p in ['Mars', 'Mercury', 'Jupiter', 'Venus', 'Saturn']:
            ph = planet_houses.get(p)
            if ph and ph in [h2, h12]:
                planets_near_moon.append(p)
        if not planets_near_moon:
            yogas.append({
                'name': 'Kemadruma Yoga',
                'description': 'No planets in 2nd or 12th from Moon — periods of hardship.',
                'planets': ['Moon'],
                'type': 'Malefic',
            })

    return yogas


# ═══════════════════════════════════════════════════════════════════════════ #
# PLANETARY DIGNITY
# ═══════════════════════════════════════════════════════════════════════════ #

def get_planetary_dignity(planet_name: str, sidereal_lon: float) -> dict:
    """Determine planetary dignity: exalted, debilitated, own sign, moolatrikona, or neutral."""
    if planet_name in ('Rahu', 'Ketu'):
        return {'status': 'Shadow Planet', 'description': 'Nodes do not have standard dignity.'}

    rashi = get_rashi(sidereal_lon)
    sign_num = rashi['index']
    deg_in_sign = rashi['degree_in_sign']

    if planet_name in EXALTATION:
        ex_sign, ex_deg = EXALTATION[planet_name]
        if sign_num == ex_sign:
            return {'status': 'Exalted', 'description': f'{planet_name} is exalted in {rashi["name"]} — maximum strength.'}

    if planet_name in DEBILITATION:
        db_sign, db_deg = DEBILITATION[planet_name]
        if sign_num == db_sign:
            return {'status': 'Debilitated', 'description': f'{planet_name} is debilitated in {rashi["name"]} — weakened.'}

    if planet_name in MOOLATRIKONA:
        mt_sign, mt_start, mt_end = MOOLATRIKONA[planet_name]
        if sign_num == mt_sign and mt_start <= deg_in_sign < mt_end:
            return {'status': 'Moolatrikona', 'description': f'{planet_name} in Moolatrikona in {rashi["name"]} — very strong.'}

    if planet_name in OWN_SIGNS:
        if sign_num in OWN_SIGNS[planet_name]:
            return {'status': 'Own Sign', 'description': f'{planet_name} in own sign {rashi["name"]} — comfortable and strong.'}

    return {'status': 'Neutral', 'description': f'{planet_name} in {rashi["name"]} — neutral placement.'}
