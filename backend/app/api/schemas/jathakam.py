"""
jathakam.py — Pydantic v2 response contracts for the jathakam endpoints.

Every v2 response is self-documenting: the ``meta`` block carries the
"Thirukanitha badge" (ephemeris, ayanamsa system and value, node
convention, precision statement) so consumers can trust the computation
without extra requests.

References:
    - docs/backend-v2-plan.md §2 (API surface, trust feature)
    - docs/01-thirukanitha-jathakam-calculation.md ("What a complete
      Thirukanitha jathakam therefore contains")
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict

# ═══════════════════════════════════════════════════════════════════════ #
# Shared building blocks
# ═══════════════════════════════════════════════════════════════════════ #


class Trilingual(BaseModel):
    """A name in the four languages used by the app.

    ``tamil``/``sinhala`` are ``None`` where the reference docs do not
    define a spelling; consumers fall back to ``english`` for display.
    """

    english: str
    sanskrit: str
    tamil: str | None = None
    sinhala: str | None = None


class EphemerisInfo(BaseModel):
    """The ephemeris used for the computation."""

    name: str
    source: str
    coverage: dict[str, str]
    accuracy: str


class AyanamsaInfo(BaseModel):
    """Ayanamsa used — the Thirukanitha badge's core trust value."""

    system: str
    value_deg: float
    definition: str


class ComputationBadge(BaseModel):
    """Self-description block present in every v2 response."""

    version: str
    tradition: str
    precision: str
    ephemeris: EphemerisInfo
    ayanamsa: AyanamsaInfo
    node_convention: str


class BirthInfo(BaseModel):
    """Echo of the resolved birth input, plus the astronomical instant."""

    date: str
    time: str
    timezone: str
    latitude: float
    longitude: float
    local_datetime: str
    utc_datetime: str
    jd_ut1: float


# ═══════════════════════════════════════════════════════════════════════ #
# Panchangam (five angas)
# ═══════════════════════════════════════════════════════════════════════ #


class TithiInfo(BaseModel):
    """The lunar day (Thithi)."""

    index: int  # 0-based (0–29)
    number: int  # 1-based (1–30)
    paksha: str  # "shukla" | "krishna"
    name: Trilingual


class VaraInfo(BaseModel):
    """The weekday (Vaaram) of the sunrise-anchored civil day."""

    index: int  # Sunday = 0
    name: Trilingual


class NakshatraInfo(BaseModel):
    """The lunar mansion (Nakshatram) the Moon occupies."""

    index: int  # 0-based (0–26)
    pada: int  # 1-based (1–4)
    lord: str  # graha id, e.g. "Moon"
    name: Trilingual


class YogaInfo(BaseModel):
    """The Sun+Moon combined-motion yoga (Yogam)."""

    index: int  # 0-based (0–26)
    name: Trilingual


class KaranaInfo(BaseModel):
    """The half-tithi (Karanam)."""

    index: int  # 0-based (0–10)
    name: Trilingual


class PanchangamInfo(BaseModel):
    """The five angas at the exact birth moment."""

    tithi: TithiInfo
    vara: VaraInfo
    nakshatra: NakshatraInfo
    yoga: YogaInfo
    karana: KaranaInfo


# ═══════════════════════════════════════════════════════════════════════ #
# Lagna, grahas, bhavas, doshas
# ═══════════════════════════════════════════════════════════════════════ #


class LagnaInfo(BaseModel):
    """The sidereal Ascendant (Lagna) at the birth instant."""

    sidereal_longitude_deg: float
    rasi_index: int
    degree_in_sign_deg: float
    rasi: Trilingual
    navamsa_rasi_index: int
    navamsa_rasi: Trilingual


class DignityInfo(BaseModel):
    """Classical dignity of a graha (Uccham / Neecham / Aatchi / neutral)."""

    dignity: str  # exalted | debilitated | moolatrikona | own_sign | neutral
    rasi_index: int
    degree_in_sign_deg: float
    distance_from_exaltation_deg: float | None


class GrahaInfo(BaseModel):
    """One graha's complete position state in the jathakam."""

    name: str
    names: Trilingual
    tropical_longitude_deg: float
    sidereal_longitude_deg: float
    rasi_index: int
    rasi: Trilingual
    degree_in_sign_deg: float
    nakshatra_index: int
    nakshatra: Trilingual
    pada: int  # 1-based
    house_number: int
    retrograde: bool
    combust: bool
    combustion_separation_deg: float | None
    distance_au: float
    dignity: DignityInfo
    navamsa_rasi_index: int
    navamsa_rasi: Trilingual
    vargottama: bool


class BhavaInfo(BaseModel):
    """One whole-sign house (Bhava)."""

    house_number: int
    rasi_index: int
    rasi: Trilingual
    lord: str  # graha id
    kendra: bool
    trikona: bool
    dusthana: bool


class ChevvaiDoshamInfo(BaseModel):
    """Chevvai (Mars) Dosham — presence and from which reference points.

    References:
        docs/01-thirukanitha-jathakam-calculation.md, §12
    """

    present: bool
    reference_count: int
    houses_from_lagna: list[int]
    houses_from_moon: list[int]
    houses_from_venus: list[int]


# ═══════════════════════════════════════════════════════════════════════ #
# Dasha (Vimshottari)
# ═══════════════════════════════════════════════════════════════════════ #


class DashaBalanceInfo(BaseModel):
    """Balance of the first Mahadasa at birth."""

    lord: str  # graha id
    lord_years: float
    balance_years: float
    balance_days: float
    fraction_remaining: float
    janma_nakshatra_index: int


class DashaPeriodInfo(BaseModel):
    """One Vimshottari period on the timeline."""

    graha: str  # graha id
    category: str  # mahadasha | antardasha | pratyantardasha
    years: float
    days: float
    start_jd: float
    end_jd: float
    start_utc: str  # ISO 8601
    end_utc: str  # ISO 8601


class DashaInfo(BaseModel):
    """The Vimshottari timeline — balance plus the requested periods."""

    year_length_days: float
    balance: DashaBalanceInfo
    periods: list[DashaPeriodInfo]


# ═══════════════════════════════════════════════════════════════════════ #
# Vargas (divisional charts)
# ═══════════════════════════════════════════════════════════════════════ #


class VargaSign(BaseModel):
    """A graha's sign in one divisional chart."""

    rasi_index: int
    rasi: Trilingual
    division_index: int


class GrahaVargas(BaseModel):
    """A graha's placements across the requested vargas."""

    name: str
    positions: dict[str, VargaSign]  # keyed by varga id, e.g. "D1", "D9"
    vargottama: bool


# ═══════════════════════════════════════════════════════════════════════ #
# Daily almanac (panchangam endpoint)
# ═══════════════════════════════════════════════════════════════════════ #


class AlmanacWindow(BaseModel):
    """One auspicious/inauspicious window of the day."""

    start_local: str
    end_local: str
    start_utc: str
    end_utc: str


class DailyAlmanac(BaseModel):
    """The full almanac of the Udaya day containing the birth instant.

    Windows are ``None`` where the Sun does not rise or set (polar
    conditions).
    """

    available: bool
    vara: VaraInfo
    sunrise_utc: str | None
    sunrise_local: str | None
    sunset_utc: str | None
    sunset_local: str | None
    next_sunrise_utc: str | None
    next_sunrise_local: str | None
    rahu_kalam: AlmanacWindow | None
    yamagandam: AlmanacWindow | None
    gulika: AlmanacWindow | None
    abhijit: AlmanacWindow | None


# ═══════════════════════════════════════════════════════════════════════ #
# Endpoint responses
# ═══════════════════════════════════════════════════════════════════════ #


class JathakamResponse(BaseModel):
    """The flagship — a complete Thirukanitha Jathakam.

    Panchangam, lagna, all nine grahas (with D1 + D9 placements and
    dignity), whole-sign bhavas, the Vimshottari mahadasha timeline and
    the Chevvai Dosham status.

    References:
        docs/01-thirukanitha-jathakam-calculation.md (complete jathakam)
    """

    model_config = ConfigDict(extra="ignore")

    meta: ComputationBadge
    birth: BirthInfo
    panchangam: PanchangamInfo
    lagna: LagnaInfo
    grahas: list[GrahaInfo]
    bhavas: list[BhavaInfo]
    dasha: DashaInfo
    chevvai_dosham: ChevvaiDoshamInfo


class PanchangamResponse(BaseModel):
    """Birth panchangam plus the daily almanac of the birth day."""

    meta: ComputationBadge
    birth: BirthInfo
    panchangam: PanchangamInfo
    almanac: DailyAlmanac


class DashaResponse(BaseModel):
    """Full Vimshottari timeline (MD/AD/PD) with the balance at birth."""

    meta: ComputationBadge
    birth: BirthInfo
    dasha: DashaInfo


class VargasResponse(BaseModel):
    """Per-graha placements in the requested divisional charts."""

    meta: ComputationBadge
    birth: BirthInfo
    grahas: list[GrahaVargas]
