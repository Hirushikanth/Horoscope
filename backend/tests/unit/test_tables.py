"""Unit tests for the trilingual reference tables (docs §4/§5/§6).

Every row of the docs' name tables is cross-checked here:

    - docs/01 §4 graha Tamil names
    - docs/02 (all tables transcribed elsewhere)
    - docs/south-indian-horoscope.md §6.1 nakshatras (Tamil + Sinhala),
      §6.2 rashis (Tamil), §6.3 tithis (Tamil)
"""

from __future__ import annotations

import pytest
from app.vedic.tables import (
    CHARA_KARANA_NAMES,
    GRAHA_NAMES,
    KARANA_NAMES,
    RASI_NAMES,
    STHIRA_KARANA_NAMES,
    TITHI_NAMES,
    VARA_NAMES,
    YOGA_NAMES,
    Graha,
    Rasi,
    TrilingualName,
    Vara,
    get_karana_name,
    get_tithi_name,
)

# ═══════════════════════════════════════════════════════════════════════ #
# docs/south-indian-horoscope.md §6.1 — 27 nakshatra names
# ═══════════════════════════════════════════════════════════════════════ #
# (sanskrit, tamil, sinhala, ruler) — the ruler column is cross-checked
# against docs/01 §9 in test_nakshatra.py.

DOCS_NAKSHATRA_NAMES = [
    ("Ashwini", "Aswini", "Aswida"),
    ("Bharani", "Bharani", "Kethi"),
    ("Krittika", "Karthigai", "Katyo"),
    ("Rohini", "Rohini", "Rehenu"),
    ("Mrigashira", "Mrigasheersham", None),
    ("Ardra", "Thiruvaathirai", "Ada"),
    ("Punarvasu", "Punarpoosam", "Punarvasu"),
    ("Pushya", "Poosam", "Pussa"),
    ("Ashlesha", "Aayilyam", "Asaleya"),
    ("Magha", "Makam", "Maka"),
    ("Purva Phalguni", "Pooram", "Pubba"),
    ("Uttara Phalguni", "Uthiram", "Utra"),
    ("Hasta", "Hastham", "Hatha"),
    ("Chitra", "Chithirai", "Siththa"),
    ("Swati", "Swaathi", "Swathi"),
    ("Vishakha", "Visaakam", "Visaka"),
    ("Anuradha", "Anusham", "Anura"),
    ("Jyeshtha", "Kettai", "Keta"),
    ("Mula", "Moolam", "Mula"),
    ("Purva Ashadha", "Pooraadam", "Poorvashada"),
    ("Uttara Ashadha", "Uthiraadam", "Uttrashada"),
    ("Shravana", "Thiruvonam", "Suvana"),
    ("Dhanishtha", "Avittam", "Avitta"),
    ("Shatabhisha", "Sadayam", "Satha"),
    ("Purva Bhadrapada", "Poorattathi", "Poorvabadrapada"),
    ("Uttara Bhadrapada", "Uthirattathi", "Uttrabadrapada"),
    ("Revati", "Revathi", "Revathi"),
]


def test_nakshatra_table_matches_docs_row_by_row():
    from app.vedic.tables import NAKSHATRA_NAMES

    assert len(NAKSHATRA_NAMES) == 27
    for index, (sanskrit, tamil, sinhala) in enumerate(DOCS_NAKSHATRA_NAMES):
        record = NAKSHATRA_NAMES[index]
        assert record.english == sanskrit, index
        assert record.tamil == tamil, index
        assert record.sinhala == sinhala, index


def test_nakshatra_rulers_match_docs_sequence():
    """docs/01 §9: Ketu → Venus → Sun → Moon → Mars → Rahu → Jupiter →
    Saturn → Mercury, repeating from Ashwini."""
    expected = ["Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"]
    from app.vedic.nakshatra import NAKSHATRA_LORDS

    assert len(NAKSHATRA_LORDS) == 27
    for index in range(27):
        assert NAKSHATRA_LORDS[index].value == expected[index % 9], index


# ═══════════════════════════════════════════════════════════════════════ #
# docs/south-indian-horoscope.md §6.2 — rashi Tamil names
# ═══════════════════════════════════════════════════════════════════════ #


def test_rasi_names_match_docs_row_by_row():
    # (english, tamil) per §6.2, in zodiac order
    docs = [
        ("Aries", "Mesham"),
        ("Taurus", "Rishabam"),
        ("Gemini", "Midhunam"),
        ("Cancer", "Kadagam"),
        ("Leo", "Simmam"),
        ("Virgo", "Kanni"),
        ("Libra", "Thulam"),
        ("Scorpio", "Vrischikam"),
        ("Sagittarius", "Dhanusu"),
        ("Capricorn", "Makaram"),
        ("Aquarius", "Kumbam"),
        ("Pisces", "Meenam"),
    ]
    assert len(RASI_NAMES) == 12
    assert len(tuple(Rasi)) == 12
    for index, (english, tamil) in enumerate(docs):
        assert RASI_NAMES[index].english == english, index
        assert RASI_NAMES[index].tamil == tamil, index


# ═══════════════════════════════════════════════════════════════════════ #
# docs/south-indian-horoscope.md §6.3 — tithi Tamil names
# ═══════════════════════════════════════════════════════════════════════ #


def test_tithi_names_match_docs():
    docs_tamil = [
        "Pradhamai",
        "Dwithiyai",
        "Trithiyai",
        "Chathurthi",
        "Panchami",
        "Shashthi",
        "Sapthami",
        "Ashtami",
        "Navami",
        "Dashami",
        "Ekadashi",
        "Dwadashi",
        "Trayodashi",
        "Chathurdashi",
        "Pournami",
    ]
    assert len(TITHI_NAMES) == 16
    for index, tamil in enumerate(docs_tamil):
        assert TITHI_NAMES[index].tamil == tamil, index
    # Shukla paksha: index 0..14 are Pratipada..Pournami
    for index in range(15):
        assert get_tithi_name(index) == TITHI_NAMES[index]
    # Krishna paksha: 15..28 reuse Pradhamai..Chathurdashi; 29 = Amavasai
    for index in range(15, 29):
        assert get_tithi_name(index) == TITHI_NAMES[index - 15]
    assert get_tithi_name(29).english == "Amavasya"
    assert get_tithi_name(29).tamil == "Amavasai"


# ═══════════════════════════════════════════════════════════════════════ #
# docs/01 §4 — graha Tamil names
# ═══════════════════════════════════════════════════════════════════════ #


def test_graha_names_match_docs():
    docs = [
        ("Sun", "சூரியன்"),
        ("Moon", "சந்திரன்"),
        ("Mars", "செவ்வாய்"),
        ("Mercury", "புதன்"),
        ("Jupiter", "குரு"),
        ("Venus", "சுக்கிரன்"),
        ("Saturn", "சனி"),
        ("Rahu", "ராகு"),
        ("Ketu", "கேது"),
    ]
    assert len(GRAHA_NAMES) == 9
    assert len(tuple(Graha)) == 9
    for index, (english, tamil) in enumerate(docs):
        assert GRAHA_NAMES[index].english == english, index
        assert GRAHA_NAMES[index].tamil == tamil, index


# ═══════════════════════════════════════════════════════════════════════ #
# Table integrity — cardinality and lookup bounds
# ═══════════════════════════════════════════════════════════════════════ #


def test_table_cardinalities():
    assert len(VARA_NAMES) == 7
    assert len(tuple(Vara)) == 7
    assert len(YOGA_NAMES) == 27
    assert len(CHARA_KARANA_NAMES) == 7
    assert len(STHIRA_KARANA_NAMES) == 4
    assert len(KARANA_NAMES) == 11
    assert get_karana_name(10).english == "Kimstughna"


@pytest.mark.parametrize("index", [0, 10, 14, 15, 26, 28, 29])
def test_tithi_name_bounds(index):
    assert isinstance(get_tithi_name(index), TrilingualName)


@pytest.mark.parametrize("bad", [-1, 30, 100])
def test_tithi_name_rejects_out_of_range(bad):
    with pytest.raises(ValueError):
        get_tithi_name(bad)


@pytest.mark.parametrize("index", list(range(27)))
def test_all_yoga_names_present(index):
    assert YOGA_NAMES[index].english


@pytest.mark.parametrize("index", list(range(11)))
def test_all_karana_names_present(index):
    assert KARANA_NAMES[index].english


def test_karana_chara_sthira_split():
    """docs/01 §5: 7 chara (movable) + 4 sthira (fixed) karanas."""
    assert [k.english for k in CHARA_KARANA_NAMES] == [
        "Bava",
        "Balava",
        "Kaulava",
        "Taitila",
        "Garaja",
        "Vanija",
        "Vishti",
    ]
    assert [k.english for k in STHIRA_KARANA_NAMES] == [
        "Shakuni",
        "Chatushpada",
        "Naga",
        "Kimstughna",
    ]
