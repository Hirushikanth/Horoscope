"""
tables.py — trilingual reference tables (English / Sanskrit / Tamil / Sinhala).

Every name table used by the Vedic layer lives here, transcribed from the
reference documents:

    - docs/01-thirukanitha-jathakam-calculation.md    §4 (grahas), §5 (panchangam)
    - docs/02-kalyana-porutham-matching.md            (gana, yoni, nadi, rajju, vedha)
    - docs/south-indian-horoscope.md                  §6.1–6.3 (trilingual names)

Conventions:

    * ``english``   — the spelling used by the reference documents.
    * ``sanskrit``  — IAST transliteration of the Sanskrit form.
    * ``tamil``     — Tamil spelling, verbatim where the documents define it.
    * ``sinhala``   — Sinhala spelling, verbatim where the documents define it
      (``None`` where the documents do not give a name; the API layer then
      falls back to the English form for display).

``Graha`` values are the exact strings used by ``astronomy.positions``
(``GRAHA_NAMES``) so the two layers interoperate without mapping tables.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

# ═══════════════════════════════════════════════════════════════════════ #
# Identity enums
# ═══════════════════════════════════════════════════════════════════════ #


class Graha(StrEnum):
    """The nine grahas. Values match ``astronomy.positions.GRAHA_NAMES``."""

    SURYA = "Sun"
    CHANDRA = "Moon"
    CHEVVAI = "Mars"
    BUDHA = "Mercury"
    GURU = "Jupiter"
    SUKRA = "Venus"
    SANI = "Saturn"
    RAHU = "Rahu"
    KETU = "Ketu"


class Rasi(StrEnum):
    """The twelve rasis. Values are the standard Vedic names (Sanskrit-derived)."""

    MESHA = "Mesha"  # Aries
    VRISHABHA = "Vrishabha"  # Taurus
    MITHUNA = "Mithuna"  # Gemini
    KARKA = "Karka"  # Cancer
    SIMHA = "Simha"  # Leo
    KANYA = "Kanya"  # Virgo
    TULA = "Tula"  # Libra
    VRISCHIKA = "Vrischika"  # Scorpio
    DHANUS = "Dhanus"  # Sagittarius
    MAKARA = "Makara"  # Capricorn
    KUMBHA = "Kumbha"  # Aquarius
    MEENA = "Meena"  # Pisces


class Vara(StrEnum):
    """The seven weekdays (Sunday-first, the panchangam order)."""

    RAVIVARA = "Sunday"
    SOMAVARA = "Monday"
    MANGALAVARA = "Tuesday"
    BUDHAVARA = "Wednesday"
    GURUVARA = "Thursday"
    SUKRAVARA = "Friday"
    SANIVARA = "Saturday"


# ═══════════════════════════════════════════════════════════════════════ #
# Trilingual name record
# ═══════════════════════════════════════════════════════════════════════ #


@dataclass(frozen=True)
class TrilingualName:
    """A name in the four languages used by the app.

    Attributes:
        english: Common English spelling (per the reference docs).
        sanskrit: IAST transliteration of the Sanskrit form.
        tamil: Tamil spelling, or ``None`` if the docs do not define one.
        sinhala: Sinhala spelling, or ``None`` if the docs do not define one.
    """

    english: str
    sanskrit: str
    tamil: str | None = None
    sinhala: str | None = None


# ═══════════════════════════════════════════════════════════════════════ #
# Nakshatras — docs/south-indian-horoscope.md §6.1 (Tamil + Sinhala)
# ═══════════════════════════════════════════════════════════════════════ #
# The English/Sanskrit spelling follows docs/01, which uses the common
# transliteration; the IAST form is given in the sanskrit field. The
# Sinhala name of Mrigashira is not defined in the docs and is ``None``.

NAKSHATRA_NAMES: tuple[TrilingualName, ...] = (
    TrilingualName("Ashwini", "Aśvinī", "Aswini", "Aswida"),
    TrilingualName("Bharani", "Bharaṇī", "Bharani", "Kethi"),
    TrilingualName("Krittika", "Kṛttikā", "Karthigai", "Katyo"),
    TrilingualName("Rohini", "Rohiṇī", "Rohini", "Rehenu"),
    TrilingualName("Mrigashira", "Mṛgaśira", "Mrigasheersham"),
    TrilingualName("Ardra", "Ārdrā", "Thiruvaathirai", "Ada"),
    TrilingualName("Punarvasu", "Punarvasu", "Punarpoosam", "Punarvasu"),
    TrilingualName("Pushya", "Puṣya", "Poosam", "Pussa"),
    TrilingualName("Ashlesha", "Āśleṣā", "Aayilyam", "Asaleya"),
    TrilingualName("Magha", "Maghā", "Makam", "Maka"),
    TrilingualName("Purva Phalguni", "Pūrva Phalgunī", "Pooram", "Pubba"),
    TrilingualName("Uttara Phalguni", "Uttara Phalgunī", "Uthiram", "Utra"),
    TrilingualName("Hasta", "Hasta", "Hastham", "Hatha"),
    TrilingualName("Chitra", "Citrā", "Chithirai", "Siththa"),
    TrilingualName("Swati", "Svātī", "Swaathi", "Swathi"),
    TrilingualName("Vishakha", "Viśākhā", "Visaakam", "Visaka"),
    TrilingualName("Anuradha", "Anurādhā", "Anusham", "Anura"),
    TrilingualName("Jyeshtha", "Jyeṣṭhā", "Kettai", "Keta"),
    TrilingualName("Mula", "Mūla", "Moolam", "Mula"),
    TrilingualName("Purva Ashadha", "Pūrvāṣāḍhā", "Pooraadam", "Poorvashada"),
    TrilingualName("Uttara Ashadha", "Uttarāṣāḍhā", "Uthiraadam", "Uttrashada"),
    TrilingualName("Shravana", "Śravaṇa", "Thiruvonam", "Suvana"),
    TrilingualName("Dhanishtha", "Dhaniṣṭhā", "Avittam", "Avitta"),
    TrilingualName("Shatabhisha", "Śatabhiṣā", "Sadayam", "Satha"),
    TrilingualName("Purva Bhadrapada", "Pūrva Bhādrapadā", "Poorattathi", "Poorvabadrapada"),
    TrilingualName("Uttara Bhadrapada", "Uttara Bhādrapadā", "Uthirattathi", "Uttrabadrapada"),
    TrilingualName("Revati", "Revatī", "Revathi", "Revathi"),
)


# ═══════════════════════════════════════════════════════════════════════ #
# Grahas — docs/01 §4 (Tamil), docs/south-indian-horoscope.md §6.1 rulers
# ═══════════════════════════════════════════════════════════════════════ #

GRAHA_NAMES: tuple[TrilingualName, ...] = (
    TrilingualName("Sun", "Sūrya", "சூரியன்"),
    TrilingualName("Moon", "Candra", "சந்திரன்"),
    TrilingualName("Mars", "Maṅgala", "செவ்வாய்"),
    TrilingualName("Mercury", "Budha", "புதன்"),
    TrilingualName("Jupiter", "Bṛhaspati", "குரு"),
    TrilingualName("Venus", "Śukra", "சுக்கிரன்"),
    TrilingualName("Saturn", "Śani", "சனி"),
    TrilingualName("Rahu", "Rāhu", "ராகு"),
    TrilingualName("Ketu", "Ketu", "கேது"),
)

#: Map ``Graha`` → trilingual record.
GRAHA_NAME_BY_ID: dict[Graha, TrilingualName] = {
    graha: record for graha, record in zip(tuple(Graha), GRAHA_NAMES, strict=True)
}


# ═══════════════════════════════════════════════════════════════════════ #
# Rashis — docs/south-indian-horoscope.md §6.2 (Tamil)
# ═══════════════════════════════════════════════════════════════════════ #

RASI_NAMES: tuple[TrilingualName, ...] = (
    TrilingualName("Aries", "Meṣa", "Mesham"),
    TrilingualName("Taurus", "Vṛṣabha", "Rishabam"),
    TrilingualName("Gemini", "Mithuna", "Midhunam"),
    TrilingualName("Cancer", "Karkaṭa", "Kadagam"),
    TrilingualName("Leo", "Siṃha", "Simmam"),
    TrilingualName("Virgo", "Kanyā", "Kanni"),
    TrilingualName("Libra", "Tulā", "Thulam"),
    TrilingualName("Scorpio", "Vṛścika", "Vrischikam"),
    TrilingualName("Sagittarius", "Dhanus", "Dhanusu"),
    TrilingualName("Capricorn", "Makara", "Makaram"),
    TrilingualName("Aquarius", "Kumbha", "Kumbam"),
    TrilingualName("Pisces", "Mīna", "Meenam"),
)

#: Map ``Rasi`` → trilingual record.
RASI_NAME_BY_ID: dict[Rasi, TrilingualName] = {
    rasi: record for rasi, record in zip(tuple(Rasi), RASI_NAMES, strict=True)
}

#: Rasi at each 30° zodiac segment (index by ``rasi_index``).
RASI_BY_INDEX: tuple[Rasi, ...] = tuple(Rasi)


# ═══════════════════════════════════════════════════════════════════════ #
# Varas — weekday names; Tamil/Sinhala are the standard Sri Lankan usage
# ═══════════════════════════════════════════════════════════════════════ #

VARA_NAMES: tuple[TrilingualName, ...] = (
    TrilingualName("Sunday", "Ravivāra", "Nyayiru", "Ira"),
    TrilingualName("Monday", "Somavāra", "Thingal", "Sanda"),
    TrilingualName("Tuesday", "Maṅgalavāra", "Sevvai", "Angaharuwa"),
    TrilingualName("Wednesday", "Budhavāra", "Budhan", "Budada"),
    TrilingualName("Thursday", "Guruvāra", "Viyalan", "Brahaspathinda"),
    TrilingualName("Friday", "Śukravāra", "Velli", "Sikuraada"),
    TrilingualName("Saturday", "Śanivāra", "Sani", "Senasuraada"),
)

#: Map ``Vara`` → trilingual record.
VARA_NAME_BY_ID: dict[Vara, TrilingualName] = {
    vara: record for vara, record in zip(tuple(Vara), VARA_NAMES, strict=True)
}


# ═══════════════════════════════════════════════════════════════════════ #
# Tithis — 15 Shukla names + Amavasya; docs/south-indian-horoscope.md §6.3
# ═══════════════════════════════════════════════════════════════════════ #

TITHI_NAMES: tuple[TrilingualName, ...] = (
    TrilingualName("Pratipada", "Pratipadā", "Pradhamai"),
    TrilingualName("Dwitiya", "Dvitīyā", "Dwithiyai"),
    TrilingualName("Tritiya", "Tṛtīyā", "Trithiyai"),
    TrilingualName("Chaturthi", "Caturthī", "Chathurthi"),
    TrilingualName("Panchami", "Pañcamī", "Panchami"),
    TrilingualName("Shashthi", "Ṣaṣṭhī", "Shashthi"),
    TrilingualName("Saptami", "Saptamī", "Sapthami"),
    TrilingualName("Ashtami", "Aṣṭamī", "Ashtami"),
    TrilingualName("Navami", "Navamī", "Navami"),
    TrilingualName("Dashami", "Daśamī", "Dashami"),
    TrilingualName("Ekadashi", "Ekādaśī", "Ekadashi"),
    TrilingualName("Dwadashi", "Dvādaśī", "Dwadashi"),
    TrilingualName("Trayodashi", "Trayodaśī", "Trayodashi"),
    TrilingualName("Chaturdashi", "Caturdaśī", "Chathurdashi"),
    TrilingualName("Purnima", "Pūrṇimā", "Pournami"),
    TrilingualName("Amavasya", "Amāvasyā", "Amavasai"),
)


def get_tithi_name(tithi_index: int) -> TrilingualName:
    """Trilingual name of the tithi at 0-based ``tithi_index`` (0–29).

    Indices 0–14 are the Shukla (waxing) half ending in Purnima; 15–28
    reuse the Pratipada–Chaturdashi names for the Krishna (waning) half;
    29 is Amavasya.

    References:
        docs/south-indian-horoscope.md, §6.3
    """
    if not 0 <= tithi_index <= 29:
        raise ValueError(f"tithi_index must be in 0..29, got {tithi_index}")
    if tithi_index <= 14:
        return TITHI_NAMES[tithi_index]
    if tithi_index == 29:
        return TITHI_NAMES[15]
    return TITHI_NAMES[tithi_index - 15]


# ═══════════════════════════════════════════════════════════════════════ #
# Yogas (27) and Karanas (11) — docs/01 §5 lists the karana names verbatim
# ═══════════════════════════════════════════════════════════════════════ #

YOGA_NAMES: tuple[TrilingualName, ...] = (
    TrilingualName("Vishkambha", "Viṣkambha"),
    TrilingualName("Priti", "Prīti"),
    TrilingualName("Ayushman", "Āyuṣmān"),
    TrilingualName("Saubhagya", "Saubhāgya"),
    TrilingualName("Shobhana", "Śobhana"),
    TrilingualName("Atiganda", "Atigaṇḍa"),
    TrilingualName("Sukarman", "Sukarman"),
    TrilingualName("Dhriti", "Dhṛti"),
    TrilingualName("Shula", "Śūla"),
    TrilingualName("Ganda", "Gaṇḍa"),
    TrilingualName("Vriddhi", "Vṛddhi"),
    TrilingualName("Dhruva", "Dhruva"),
    TrilingualName("Vyaghata", "Vyāghāta"),
    TrilingualName("Harshana", "Harṣaṇa"),
    TrilingualName("Vajra", "Vajra"),
    TrilingualName("Siddhi", "Siddhi"),
    TrilingualName("Vyatipata", "Vyatīpāta"),
    TrilingualName("Variyana", "Varīyān"),
    TrilingualName("Parigha", "Parigha"),
    TrilingualName("Shiva", "Śiva"),
    TrilingualName("Siddha", "Siddha"),
    TrilingualName("Sadhya", "Sādhya"),
    TrilingualName("Shubha", "Śubha"),
    TrilingualName("Shukla", "Śukla"),
    TrilingualName("Brahma", "Brahma"),
    TrilingualName("Indra", "Indra"),
    TrilingualName("Vaidhriti", "Vaidhṛti"),
)

# 7 movable (chara) karanas — docs/01 §5 lists them in this exact order.
CHARA_KARANA_NAMES: tuple[TrilingualName, ...] = (
    TrilingualName("Bava", "Bava"),
    TrilingualName("Balava", "Bālava"),
    TrilingualName("Kaulava", "Kaulava"),
    TrilingualName("Taitila", "Taitila"),
    TrilingualName("Garaja", "Garaja"),
    TrilingualName("Vanija", "Vaṇija"),
    TrilingualName("Vishti", "Viṣṭi"),
)

# 4 fixed (sthira) karanas — occur once each at the month's Amavasya junction.
STHIRA_KARANA_NAMES: tuple[TrilingualName, ...] = (
    TrilingualName("Shakuni", "Śakuni"),
    TrilingualName("Chatushpada", "Catuṣpāda"),
    TrilingualName("Naga", "Nāga"),
    TrilingualName("Kimstughna", "Kiṃstughna"),
)

#: All 11 karanas: the 7 chara followed by the 4 sthira.
KARANA_NAMES: tuple[TrilingualName, ...] = (
    *CHARA_KARANA_NAMES,
    *STHIRA_KARANA_NAMES,
)


def get_yoga_name(yoga_index: int) -> TrilingualName:
    """Trilingual name of the yoga at 0-based ``yoga_index`` (0–26)."""
    if not 0 <= yoga_index <= 26:
        raise ValueError(f"yoga_index must be in 0..26, got {yoga_index}")
    return YOGA_NAMES[yoga_index]


def get_karana_name(karana_index: int) -> TrilingualName:
    """Trilingual name of the karana at 0-based ``karana_index`` (0–10)."""
    if not 0 <= karana_index <= 10:
        raise ValueError(f"karana_index must be in 0..10, got {karana_index}")
    return KARANA_NAMES[karana_index]
