"""
poruthams.py — the eleven Kalyana Porutham checks.

Implements, strictly and mechanically, every rule of the Tamil/South
Indian pathu-porutham (பத்து பொருத்தம்) system exactly as transcribed in
docs/02: dina, gana, mahendra, stree deergha, yoni, rasi, rasi
athipathi, vashya, rajju, vedha — plus nadi as the traditional eleventh
factor. All counting is inclusive from the bride's nakshatra/rasi to the
groom's, wrapping after 27 nakshatras / 12 rasis.

Each check takes a :class:`MatchingInput` for each partner (the minimal
data extracted from their jathakams) and returns a
:class:`PoruthamReport` with a :class:`PoruthamResult`, the rule-relevant
detail values and any notes (exceptions applied).

References:
    docs/02-kalyana-porutham-matching.md — §1 (Dina), §2 (Gana),
    §3 (Mahendra), §4 (Stree Deergha), §5 (Yoni), §6 (Rasi),
    §7 (Rasi Athipathi), §8 (Vashya), §9 (Rajju), §10 (Vedha),
    and the Nadi table.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any

import numpy as np

from app.vedic.nakshatra import (
    Gana,
    get_nakshatra_gana,
    get_nakshatra_nadi,
    get_nakshatra_rajju,
    get_nakshatra_yoni,
    is_vedha_pair,
    yonis_are_enemies,
)
from app.vedic.rashi import (
    MaitriRelation,
    VashyaGroup,
    get_mutual_maitri,
    get_rasi_lord,
    get_vashya_group,
)
from app.vedic.tables import TrilingualName

# ═══════════════════════════════════════════════════════════════════════ #
# Result enum and report
# ═══════════════════════════════════════════════════════════════════════ #


class PoruthamResult(StrEnum):
    """The three classical verdict levels of one porutham — docs/02 scoring.

    ``score`` is Uthamam = 1, Madhyamam = ½, Athamam = 0 (float64).
    """

    UTHAMAM = "uthamam"
    MADHYAMAM = "madhyamam"
    ATHAMAM = "athamam"

    @property
    def score(self) -> np.float64:
        """The numeric score of this result (Uthamam 1, Madhyamam ½, Athamam 0)."""
        if self is PoruthamResult.UTHAMAM:
            return np.float64(1.0)
        if self is PoruthamResult.MADHYAMAM:
            return np.float64(0.5)
        return np.float64(0.0)


@dataclass(frozen=True)
class PoruthamReport:
    """The outcome of one porutham check for a bride/groom pair.

    Attributes:
        id: Stable machine id of the porutham (e.g. ``"dina"``).
        result: The classical verdict level.
        in_total: True when the check counts toward the 10-point total
            (``False`` only for nadi, the traditional "+" eleventh factor).
        detail: Rule-specific values — counts, groups, lords, flags.
        notes: Human-readable notes about exceptions or judgement calls.
    """

    id: str
    result: PoruthamResult
    in_total: bool
    detail: dict[str, Any]
    notes: list[str] = field(default_factory=list)


#: Trilingual names of the eleven poruthams (docs/02 headings).
PORUTHAM_NAMES: dict[str, TrilingualName] = {
    "dina": TrilingualName("Dina", "Dina", "தினம்"),
    "gana": TrilingualName("Gana", "Gaṇa", "கணம்"),
    "mahendra": TrilingualName("Mahendra", "Mahendra", "மகேந்திரம்"),
    "stree_deergha": TrilingualName("Stree Deergha", "Strī Dīrgha", "ஸ்திரீ தீர்க்கம்"),
    "yoni": TrilingualName("Yoni", "Yoni", "யோனி"),
    "rasi": TrilingualName("Rasi", "Rāśi", "ராசி"),
    "rasi_athipathi": TrilingualName("Rasi Athipathi", "Rāśi Adhipati", "ராசி அதிபதி"),
    "vashya": TrilingualName("Vashya", "Vaśya", "வசியம்"),
    "rajju": TrilingualName("Rajju", "Rajju", "ரஜ்ஜு"),
    "vedha": TrilingualName("Vedha", "Vedha", "வேதை"),
    "nadi": TrilingualName("Nadi", "Nāḍī", "நாடி"),
}

#: What each porutham governs (docs/02 summary table).
PORUTHAM_GOVERNS: dict[str, str] = {
    "dina": "Health, freedom from poverty and disease",
    "gana": "Temperament and behaviour",
    "mahendra": "Progeny and family prosperity",
    "stree_deergha": "Bride's longevity and sustained wellbeing",
    "yoni": "Physical and instinctive compatibility",
    "rasi": "Nature, and progeny",
    "rasi_athipathi": "Unity of mind and decisions",
    "vashya": "Mutual attraction and influence",
    "rajju": "Longevity of the marriage and the husband",
    "vedha": "Mutual obstruction (afflicting nakshatras)",
    "nadi": "Genetic/constitutional compatibility of children",
}


@dataclass(frozen=True)
class MatchingInput:
    """The minimal per-partner inputs needed for all eleven checks.

    Extracted by the service layer from each partner's Thirukanitha
    Jathakam (docs/02 §0): the Janma Nakshatra + Pada, the Chandra Rasi
    (Moon sign) and the Chevvai Dosham status.

    Attributes:
        nakshatra_index: Janma nakshatra, 0-based (0–26).
        pada: Janma nakshatra pada, 1-based (1–4) — reported only.
        rasi_index: Chandra rasi, 0-based (0–11).
        moon_degree_in_sign: Moon's degree within the rasi [0, 30) —
            needed only for the half-sign vashya groups (Dhanus, Makara).
        chevvai_dosham: True when the partner's chart carries Chevvai
            Dosham (cross-check only).
    """

    nakshatra_index: int
    pada: int
    rasi_index: int
    moon_degree_in_sign: np.float64
    chevvai_dosham: bool


# ═══════════════════════════════════════════════════════════════════════ #
# Counting helpers — inclusive bride → groom, wrapping
# ═══════════════════════════════════════════════════════════════════════ #


def nakshatra_count(bride: MatchingInput, groom: MatchingInput) -> int:
    """Inclusive count from the bride's nakshatra to the groom's (1–27)."""
    return (groom.nakshatra_index - bride.nakshatra_index) % 27 + 1


def rasi_count(bride: MatchingInput, groom: MatchingInput) -> int:
    """Inclusive count from the bride's rasi to the groom's (1–12)."""
    return (groom.rasi_index - bride.rasi_index) % 12 + 1


#: Tara (star) group per ``count % 9`` — remainder 0 reads as 9.
#: Docs/02 §1: 1 Janma, 2 Sampat, 3 Vipat, 4 Kshema, 5 Pratyak,
#: 6 Sadhaka, 7 Naidhana, 8 Mitra, 9 Parama Mitra.
TARA_GROUPS: dict[int, str] = {
    1: "Janma",
    2: "Sampat",
    3: "Vipat",
    4: "Kshema",
    5: "Pratyak",
    6: "Sadhaka",
    7: "Naidhana",
    8: "Mitra",
    9: "Parama Mitra",
}

#: Counts (of 27) whose Tara group is auspicious: remainder 2, 4, 6, 8
#: or 9 (Parama Mitra). Docs/02 §1 lists 2, 4, 6, 8, 9, 11, 13, 15, 18,
#: 20, 24, 26 (and 27, which the mathematical rule also admits).
AUSPICIOUS_DINA_REMAINDERS: frozenset[int] = frozenset({2, 4, 6, 8, 9})
#: Inauspicious Tara remainders (Vipat / Pratyak / Naidhana).
IN_AUSPICIOUS_DINA_REMAINDERS: frozenset[int] = frozenset({3, 5, 7})

#: Same-nakshatra (Aega Nakshatram) pairs treated as Uthamam — docs/02 §1.
AEGA_NAKSHATRAM_UTHAMAM: frozenset[int] = frozenset(
    {3, 5, 7, 9, 12, 21}  # Rohini, Ardra, Pushya, Magha, Hasta, Shravana
)
#: Same-nakshatra pairs treated as Madhyamam — docs/02 §1.
AEGA_NAKSHATRAM_MADHYAMAM: frozenset[int] = frozenset(
    {
        0,  # Ashwini
        1,  # Bharani
        2,  # Krittika
        4,  # Mrigashira
        6,  # Punarvasu
        11,  # Uttara Phalguni
        13,  # Chitra
        16,  # Anuradha
    }
)

#: Mahendra counts (of 27) — docs/02 §3.
MAHENDRA_COUNTS: frozenset[int] = frozenset({4, 7, 10, 13, 16, 19, 22, 25})

#: Stree Deergha thresholds (of 27) — docs/02 §4.
STREE_DEERGHA_UTHAMAM_MIN: int = 13
STREE_DEERGHA_MADHYAMAM_MIN: int = 7

#: Good rasi-count positions — docs/02 §6.
AUSPICIOUS_RASI_COUNTS: frozenset[int] = frozenset({1, 3, 4, 5, 7, 9, 10, 11})
#: Bad rasi-count positions (2, 6, 8, 12); 6 and 8 are Sashtashtaka.
IN_AUSPICIOUS_RASI_COUNTS: frozenset[int] = frozenset({2, 6, 8, 12})

#: Shared nakshatras for which the Eka Rasi ordering restriction is
#: waived — docs/02 §6.
EKA_RASI_EXEMPT_NAKSHATRAS: frozenset[int] = frozenset(
    {
        0,  # Ashwini
        2,  # Krittika
        3,  # Rohini
        9,  # Magha
        12,  # Hasta
        14,  # Swati
        19,  # Purva Ashadha
        23,  # Shatabhisha
    }
)

#: Vashya food-chain pairs — docs/02 §8.
VASHYA_FOOD_CHAINS: frozenset[frozenset[VashyaGroup]] = frozenset(
    {
        frozenset({VashyaGroup.JALACHARA, VashyaGroup.MANAVA}),
        frozenset({VashyaGroup.CHATUSHPADA, VashyaGroup.VANACHARA}),
    }
)


# ═══════════════════════════════════════════════════════════════════════ #
# The eleven checks — each returns a PoruthamReport
# ═══════════════════════════════════════════════════════════════════════ #


def dina_porutham(bride: MatchingInput, groom: MatchingInput) -> PoruthamReport:
    """Dina — the Tara (star) groups of the inclusive nakshatra count.

    Counts from the bride's nakshatra to the groom's; the remainder of
    the count divided by 9 places the pair in one of the nine Tara
    groups. Sampat, Kshema, Sadhaka, Mitra and Parama Mitra are Uthamam;
    Vipat, Pratyak and Naidhana are Athamam; Janma is neutral.

    Same-nakshatra (Aega Nakshatram) pairs follow the docs' explicit
    Uthamam/Madhyamam lists; the remaining same-star pairs ("weighed
    case by case" in the docs) are conservatively scored Madhyamam.

    References:
        docs/02-kalyana-porutham-matching.md, §1
    """
    count = nakshatra_count(bride, groom)
    notes: list[str] = []

    if bride.nakshatra_index == groom.nakshatra_index:
        shared = bride.nakshatra_index
        if shared in AEGA_NAKSHATRAM_UTHAMAM:
            result = PoruthamResult.UTHAMAM
        elif shared in AEGA_NAKSHATRAM_MADHYAMAM:
            result = PoruthamResult.MADHYAMAM
        else:
            result = PoruthamResult.MADHYAMAM
            notes.append(
                "Same nakshatra (Aega Nakshatram) not in the docs' explicit "
                "lists — weighed case by case; conservatively Madhyamam."
            )
        return PoruthamReport(
            id="dina",
            result=result,
            in_total=True,
            detail={"count": count, "aega_nakshatram": True},
            notes=notes,
        )

    remainder = count % 9 or 9
    tara = TARA_GROUPS[remainder]
    if remainder in AUSPICIOUS_DINA_REMAINDERS:
        result = PoruthamResult.UTHAMAM
    elif remainder in IN_AUSPICIOUS_DINA_REMAINDERS:
        result = PoruthamResult.ATHAMAM
    else:
        result = PoruthamResult.MADHYAMAM
        notes.append(
            f"Janma tara (count {count}) is neutral in the tradition — "
            "treated as Madhyamam pending astrologer judgement."
        )
    return PoruthamReport(
        id="dina",
        result=result,
        in_total=True,
        detail={"count": count, "tara_remainder": remainder, "tara": tara},
        notes=notes,
    )


def gana_porutham(bride: MatchingInput, groom: MatchingInput) -> PoruthamReport:
    """Gana — the Deva / Manushya / Rakshasa temperament compatibility.

    Deva–Deva, Manushya–Manushya and Deva–Manushya are Uthamam;
    Rakshasa–Rakshasa and Manushya–Rakshasa are Madhyamam; Deva–Rakshasa
    is the one Athamam combination. The pairing table is symmetric.

    References:
        docs/02-kalyana-porutham-matching.md, §2
    """
    bride_gana = get_nakshatra_gana(bride.nakshatra_index)
    groom_gana = get_nakshatra_gana(groom.nakshatra_index)

    pair = frozenset({bride_gana, groom_gana})
    if Gana.RAKSHASA not in pair:
        result = PoruthamResult.UTHAMAM
    elif pair == frozenset({Gana.DEVA, Gana.RAKSHASA}):
        result = PoruthamResult.ATHAMAM
    else:
        result = PoruthamResult.MADHYAMAM

    notes = []
    if bride_gana is groom_gana and bride_gana is Gana.RAKSHASA:
        notes.append(
            "Rakshasa–Rakshasa — some astrologers rate this Uthamam, "
            "others cautiously; docs/02 scores Madhyamam."
        )

    return PoruthamReport(
        id="gana",
        result=result,
        in_total=True,
        detail={"bride_gana": bride_gana.value, "groom_gana": groom_gana.value},
        notes=notes,
    )


def mahendra_porutham(bride: MatchingInput, groom: MatchingInput) -> PoruthamReport:
    """Mahendra — progeny and family prosperity.

    Uthamam when the inclusive bride→groom count is 4, 7, 10, 13, 16,
    19, 22 or 25; any other count is Athamam.

    References:
        docs/02-kalyana-porutham-matching.md, §3
    """
    count = nakshatra_count(bride, groom)
    result = PoruthamResult.UTHAMAM if count in MAHENDRA_COUNTS else PoruthamResult.ATHAMAM
    return PoruthamReport(
        id="mahendra",
        result=result,
        in_total=True,
        detail={"count": count},
        notes=[],
    )


def stree_deergha_porutham(bride: MatchingInput, groom: MatchingInput) -> PoruthamReport:
    """Stree Deergha — the bride's longevity and sustained prosperity.

    Count of 13+ is Uthamam; 7–12 is Madhyamam (sufficient to proceed);
    below 7 is Athamam.

    References:
        docs/02-kalyana-porutham-matching.md, §4
    """
    count = nakshatra_count(bride, groom)
    if count >= STREE_DEERGHA_UTHAMAM_MIN:
        result = PoruthamResult.UTHAMAM
    elif count >= STREE_DEERGHA_MADHYAMAM_MIN:
        result = PoruthamResult.MADHYAMAM
    else:
        result = PoruthamResult.ATHAMAM
    return PoruthamReport(
        id="stree_deergha",
        result=result,
        in_total=True,
        detail={"count": count},
        notes=[],
    )


def yoni_porutham(bride: MatchingInput, groom: MatchingInput) -> PoruthamReport:
    """Yoni — physical compatibility via the 14 animal yonis.

    Same yoni with opposite gender slots is Uthamam; same yoni with the
    same gender is Madhyamam (docs read it as Uthamam/Madhyamam — the
    conservative Madhyamam is applied); different non-enemy yonis are
    Madhyamam; the seven traditional enemy pairs are Athamam.

    References:
        docs/02-kalyana-porutham-matching.md, §5
    """
    bride_yoni = get_nakshatra_yoni(bride.nakshatra_index)
    groom_yoni = get_nakshatra_yoni(groom.nakshatra_index)

    notes: list[str] = []
    if bride_yoni.yoni is groom_yoni.yoni:
        if bride_yoni.gender != groom_yoni.gender:
            result = PoruthamResult.UTHAMAM
        else:
            result = PoruthamResult.MADHYAMAM
            notes.append(
                "Same yoni with the same gender slot — docs/02 reads this "
                "Uthamam/Madhyamam; the conservative Madhyamam is applied."
            )
    elif yonis_are_enemies(bride_yoni.yoni, groom_yoni.yoni):
        result = PoruthamResult.ATHAMAM
    else:
        result = PoruthamResult.MADHYAMAM

    return PoruthamReport(
        id="yoni",
        result=result,
        in_total=True,
        detail={
            "bride_yoni": bride_yoni.yoni.value,
            "groom_yoni": groom_yoni.yoni.value,
            "bride_gender": bride_yoni.gender,
            "groom_gender": groom_yoni.gender,
            "enemy_pair": result is PoruthamResult.ATHAMAM,
        },
        notes=notes,
    )


def rasi_porutham(bride: MatchingInput, groom: MatchingInput) -> PoruthamReport:
    """Rasi — Chandra rasi (Moon sign) compatibility.

    Counts of 1, 3, 4, 5, 7, 9, 10, 11 are Uthamam (7 is best); counts
    2, 6, 8, 12 are Athamam (6 and 8 are Sashtashtaka Dosham). Eka Rasi
    (count 1) additionally requires the bride's nakshatra not to fall
    before the groom's within the shared rasi — waived when the bride's
    own nakshatra is one of the eight listed stars.

    References:
        docs/02-kalyana-porutham-matching.md, §6
    """
    count = rasi_count(bride, groom)
    notes: list[str] = []
    result: PoruthamResult

    if count in AUSPICIOUS_RASI_COUNTS:
        result = PoruthamResult.UTHAMAM
        if count == 1 and bride.rasi_index == groom.rasi_index:
            bride_before_groom = bride.nakshatra_index < groom.nakshatra_index
            if bride_before_groom and bride.nakshatra_index in EKA_RASI_EXEMPT_NAKSHATRAS:
                notes.append(
                    "Eka Rasi ordering restriction waived — the bride's "
                    "nakshatra is in the docs' exemption list."
                )
            elif bride_before_groom:
                result = PoruthamResult.ATHAMAM
                notes.append(
                    "Eka Rasi (same rasi) with the bride's nakshatra falling "
                    "before the groom's within the shared rasi — Athamam."
                )
    else:
        result = PoruthamResult.ATHAMAM

    return PoruthamReport(
        id="rasi",
        result=result,
        in_total=True,
        detail={
            "count": count,
            "eka_rasi": count == 1 and bride.rasi_index == groom.rasi_index,
            "sashtashtaka": count in (6, 8),
        },
        notes=notes,
    )


def rasi_athipathi_porutham(bride: MatchingInput, groom: MatchingInput) -> PoruthamReport:
    """Rasi Athipathi — unity of mind through the Panchadha Maitri.

    Both rasi lords mutually friends (or the same graha rules both
    rasis) is Uthamam; mixed or both-neutral is Madhyamam; mutually
    enemies is Athamam.

    References:
        docs/02-kalyana-porutham-matching.md, §7
    """
    bride_lord = get_rasi_lord(bride.rasi_index)
    groom_lord = get_rasi_lord(groom.rasi_index)
    relation = get_mutual_maitri(bride_lord, groom_lord)

    if relation is MaitriRelation.FRIEND:
        result = PoruthamResult.UTHAMAM
    elif relation is MaitriRelation.ENEMY:
        result = PoruthamResult.ATHAMAM
    else:
        result = PoruthamResult.MADHYAMAM

    return PoruthamReport(
        id="rasi_athipathi",
        result=result,
        in_total=True,
        detail={
            "bride_lord": bride_lord.value,
            "groom_lord": groom_lord.value,
            "relationship": relation.value,
        },
        notes=[],
    )


def vashya_porutham(bride: MatchingInput, groom: MatchingInput) -> PoruthamReport:
    """Vashya — mutual attraction via the five vashya groups.

    Same group is Uthamam; the food-chain pairs (Jalachara↔Manava and
    Chatushpada↔Vanachara) are Athamam; any other combination is
    Madhyamam. The degree-dependent half-signs (Dhanus, Makara) use each
    partner's Moon degree within the sign.

    References:
        docs/02-kalyana-porutham-matching.md, §8
    """
    bride_group = get_vashya_group(bride.rasi_index, bride.moon_degree_in_sign)
    groom_group = get_vashya_group(groom.rasi_index, groom.moon_degree_in_sign)

    if bride_group is groom_group:
        result = PoruthamResult.UTHAMAM
    elif frozenset({bride_group, groom_group}) in VASHYA_FOOD_CHAINS:
        result = PoruthamResult.ATHAMAM
    else:
        result = PoruthamResult.MADHYAMAM

    return PoruthamReport(
        id="vashya",
        result=result,
        in_total=True,
        detail={
            "bride_group": bride_group.value,
            "groom_group": groom_group.value,
            "food_chain": frozenset({bride_group, groom_group}) in VASHYA_FOOD_CHAINS,
        },
        notes=[],
    )


def rajju_porutham(bride: MatchingInput, groom: MatchingInput) -> PoruthamReport:
    """Rajju — marriage longevity (pass/fail gate).

    Same rajju group is Athamam (Rajju Dosham); different groups are
    Uthamam. Rajju is one of the poruthams the docs treat as closer to a
    pass/fail gate than a scored factor.

    References:
        docs/02-kalyana-porutham-matching.md, §9
    """
    bride_rajju = get_nakshatra_rajju(bride.nakshatra_index)
    groom_rajju = get_nakshatra_rajju(groom.nakshatra_index)

    same_rajju = bride_rajju is groom_rajju
    result = PoruthamResult.ATHAMAM if same_rajju else PoruthamResult.UTHAMAM
    return PoruthamReport(
        id="rajju",
        result=result,
        in_total=True,
        detail={
            "bride_rajju": bride_rajju.value,
            "groom_rajju": groom_rajju.value,
            "same_group": same_rajju,
        },
        notes=[],
    )


def vedha_porutham(bride: MatchingInput, groom: MatchingInput) -> PoruthamReport:
    """Vedha — mutual nakshatra affliction (pass/fail gate).

    If the two nakshatras form a vedha pair (in either direction) the
    result is Athamam regardless of everything else; otherwise Uthamam.
    Chitra has no vedha partner.

    References:
        docs/02-kalyana-porutham-matching.md, §10
    """
    afflicted = is_vedha_pair(bride.nakshatra_index, groom.nakshatra_index)
    result = PoruthamResult.ATHAMAM if afflicted else PoruthamResult.UTHAMAM
    return PoruthamReport(
        id="vedha",
        result=result,
        in_total=True,
        detail={"vedha_pair": afflicted},
        notes=[],
    )


def nadi_porutham(bride: MatchingInput, groom: MatchingInput) -> PoruthamReport:
    """Nadi — the traditional eleventh check (genetic/constitutional).

    Different nadis are Uthamam; the same nadi is Athamam (Nadi Dosham).
    The docs note that classical texts recognise cancellation conditions
    that are left to an experienced astrologer's judgement, so no
    mechanical cancellation is applied here. Nadi does not count toward
    the 10-point total (``in_total`` is ``False``).

    References:
        docs/02-kalyana-porutham-matching.md — "Nadi Porutham" section
    """
    bride_nadi = get_nakshatra_nadi(bride.nakshatra_index)
    groom_nadi = get_nakshatra_nadi(groom.nakshatra_index)

    same_nadi = bride_nadi is groom_nadi
    result = PoruthamResult.ATHAMAM if same_nadi else PoruthamResult.UTHAMAM
    notes = (
        [
            "Same nadi (Nadi Dosham) — classical cancellation conditions "
            "exist but require astrologer judgement; none applied mechanically."
        ]
        if same_nadi
        else []
    )
    return PoruthamReport(
        id="nadi",
        result=result,
        in_total=False,
        detail={"bride_nadi": bride_nadi.value, "groom_nadi": groom_nadi.value},
        notes=notes,
    )


#: The eleven checks in their traditional order (the ten poruthams
#: followed by nadi, the additional factor).
ALL_PORUTHAMS: tuple[Callable[[MatchingInput, MatchingInput], PoruthamReport], ...] = (
    dina_porutham,
    gana_porutham,
    mahendra_porutham,
    stree_deergha_porutham,
    yoni_porutham,
    rasi_porutham,
    rasi_athipathi_porutham,
    vashya_porutham,
    rajju_porutham,
    vedha_porutham,
    nadi_porutham,
)


def compute_all_poruthams(bride: MatchingInput, groom: MatchingInput) -> dict[str, PoruthamReport]:
    """Run all eleven checks for a pair, keyed by porutham id."""
    reports: dict[str, PoruthamReport] = {}
    for check in ALL_PORUTHAMS:
        report = check(bride, groom)
        reports[report.id] = report
    return reports
