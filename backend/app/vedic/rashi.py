"""
rashi.py — the twelve rasis: lordship, vashya groups and Panchadha Maitri.

The rasi is the Moon sign — the primary zodiac reference in the Tamil
tradition — and the rasi lord ("Rasi Athipathi") drives the Rasi Athipathi
porutham; the vashya groups drive the Vashya porutham.

References:
    - docs/01-thirukanitha-jathakam-calculation.md   §9 (rasi lords)
    - docs/02-kalyana-porutham-matching.md           §7 (Panchadha Maitri),
      §8 (vashya groups)
"""

from __future__ import annotations

from enum import StrEnum

import numpy as np

from app.vedic.tables import Graha

#: Rasi span in degrees (float64).
RASI_SPAN_DEG: np.float64 = np.float64(30.0)

#: Ruling graha of each rasi (Rasi Athipathi), index by ``rasi_index``.
RASI_LORDS: tuple[Graha, ...] = (
    Graha.CHEVVAI,  # Mesha (Aries) — Mars
    Graha.SUKRA,  # Vrishabha (Taurus) — Venus
    Graha.BUDHA,  # Mithuna (Gemini) — Mercury
    Graha.CHANDRA,  # Karka (Cancer) — Moon
    Graha.SURYA,  # Simha (Leo) — Sun
    Graha.BUDHA,  # Kanya (Virgo) — Mercury
    Graha.SUKRA,  # Tula (Libra) — Venus
    Graha.CHEVVAI,  # Vrischika (Scorpio) — Mars
    Graha.GURU,  # Dhanus (Sagittarius) — Jupiter
    Graha.SANI,  # Makara (Capricorn) — Saturn
    Graha.SANI,  # Kumbha (Aquarius) — Saturn
    Graha.GURU,  # Meena (Pisces) — Jupiter
)


class VashyaGroup(StrEnum):
    """The five vashya groups — docs/02 §8.

    ``Dhanus`` and ``Makara`` belong to two groups depending on the
    degree within the sign, so group lookup is degree-dependent.
    """

    CHATUSHPADA = "chatushpada"  # quadruped
    MANAVA = "manava"  # human
    JALACHARA = "jalachara"  # aquatic
    VANACHARA = "vanachara"  # wild
    KEETA = "keeta"  # insect


class MaitriRelation(StrEnum):
    """Directed planetary relationship in the Panchadha Maitri table."""

    FRIEND = "friend"
    NEUTRAL = "neutral"
    ENEMY = "enemy"


#: Panchadha Maitri — directed friend/neutral/enemy lists per graha,
#: transcribed exactly from docs/02 §7. Rahu and Ketu do not participate
#: in the table (only rasi lords, which are always among the seven).
PANCHADHA_MAITRI: dict[Graha, dict[MaitriRelation, frozenset[Graha]]] = {
    Graha.SURYA: {
        MaitriRelation.FRIEND: frozenset({Graha.CHANDRA, Graha.CHEVVAI, Graha.GURU}),
        MaitriRelation.NEUTRAL: frozenset({Graha.BUDHA}),
        MaitriRelation.ENEMY: frozenset({Graha.SUKRA, Graha.SANI}),
    },
    Graha.CHANDRA: {
        MaitriRelation.FRIEND: frozenset({Graha.SURYA, Graha.BUDHA}),
        MaitriRelation.NEUTRAL: frozenset({Graha.CHEVVAI, Graha.GURU, Graha.SUKRA, Graha.SANI}),
        MaitriRelation.ENEMY: frozenset(),
    },
    Graha.CHEVVAI: {
        MaitriRelation.FRIEND: frozenset({Graha.SURYA, Graha.CHANDRA, Graha.GURU}),
        MaitriRelation.NEUTRAL: frozenset({Graha.SUKRA, Graha.SANI}),
        MaitriRelation.ENEMY: frozenset({Graha.BUDHA}),
    },
    Graha.BUDHA: {
        MaitriRelation.FRIEND: frozenset({Graha.SURYA, Graha.SUKRA}),
        MaitriRelation.NEUTRAL: frozenset({Graha.CHEVVAI, Graha.GURU, Graha.SANI}),
        MaitriRelation.ENEMY: frozenset({Graha.CHANDRA}),
    },
    Graha.GURU: {
        MaitriRelation.FRIEND: frozenset({Graha.SURYA, Graha.CHANDRA, Graha.CHEVVAI}),
        MaitriRelation.NEUTRAL: frozenset({Graha.SANI}),
        MaitriRelation.ENEMY: frozenset({Graha.BUDHA, Graha.SUKRA}),
    },
    Graha.SUKRA: {
        MaitriRelation.FRIEND: frozenset({Graha.BUDHA, Graha.SANI}),
        MaitriRelation.NEUTRAL: frozenset({Graha.CHEVVAI, Graha.GURU}),
        MaitriRelation.ENEMY: frozenset({Graha.SURYA, Graha.CHANDRA}),
    },
    Graha.SANI: {
        MaitriRelation.FRIEND: frozenset({Graha.BUDHA, Graha.SUKRA}),
        MaitriRelation.NEUTRAL: frozenset({Graha.GURU}),
        MaitriRelation.ENEMY: frozenset({Graha.SURYA, Graha.CHANDRA, Graha.CHEVVAI}),
    },
}

#: Rasis of each vashya group for the degree-independent signs; the
#: half-sign rasis (Dhanus, Makara) are handled by ``get_vashya_group``.
VASHYA_FULL_SIGNS: dict[VashyaGroup, frozenset[int]] = {
    VashyaGroup.CHATUSHPADA: frozenset({0, 1}),  # Mesha, Vrishabha
    VashyaGroup.MANAVA: frozenset({2, 5, 6, 10}),  # Mithuna, Kanya, Tula, Kumbha
    VashyaGroup.JALACHARA: frozenset({3, 11}),  # Karka, Meena
    VashyaGroup.VANACHARA: frozenset({4}),  # Simha (alone)
    VashyaGroup.KEETA: frozenset({7}),  # Vrischika (alone)
}


def get_rasi_index(sidereal_longitude: np.float64) -> int:
    """0-based rasi index of a sidereal longitude (0–11)."""
    normalized = np.float64(sidereal_longitude) % np.float64(360.0)
    return int(normalized // RASI_SPAN_DEG)


def get_rasi_lord(rasi_index: int) -> Graha:
    """Ruling graha (Rasi Athipathi) of the rasi.

    References:
        docs/01-thirukanitha-jathakam-calculation.md, §9
    """
    if not 0 <= rasi_index <= 11:
        raise ValueError(f"rasi_index must be in 0..11, got {rasi_index}")
    return RASI_LORDS[rasi_index]


def get_vashya_group(rasi_index: int, degree_in_sign: np.float64) -> VashyaGroup:
    """Vashya group of a rasi position — docs/02 §8.

    ``Dhanus`` (8) is Manava in its first half and Chatushpada in its
    second; ``Makara`` (9) is Chatushpada in its first half and
    Jalachara in its second. All other signs belong to a single group.

    References:
        docs/02-kalyana-porutham-matching.md, §8
    """
    if not 0 <= rasi_index <= 11:
        raise ValueError(f"rasi_index must be in 0..11, got {rasi_index}")
    if not 0.0 <= float(degree_in_sign) < 30.0:
        raise ValueError(f"degree_in_sign must be in [0, 30), got {float(degree_in_sign)}")

    for group, signs in VASHYA_FULL_SIGNS.items():
        if rasi_index in signs:
            return group

    if rasi_index == 8:  # Dhanus
        return VashyaGroup.MANAVA if float(degree_in_sign) < 15.0 else VashyaGroup.CHATUSHPADA
    if rasi_index == 9:  # Makara
        return VashyaGroup.CHATUSHPADA if float(degree_in_sign) < 15.0 else VashyaGroup.JALACHARA
    raise AssertionError("unreachable: all rasi indices are covered")


def get_maitri_relation(lord: Graha, other: Graha) -> MaitriRelation:
    """Directed relationship of ``lord`` toward ``other``.

    Rahu and Ketu do not appear in the Panchadha Maitri table (only the
    seven physical grahas rule rasis), so they are rejected.

    References:
        docs/02-kalyana-porutham-matching.md, §7
    """
    if lord in (Graha.RAHU, Graha.KETU) or other in (Graha.RAHU, Graha.KETU):
        raise ValueError(
            "Panchadha Maitri covers only the seven physical grahas, "
            f"got lord={lord.value}, other={other.value}"
        )
    row = PANCHADHA_MAITRI[lord]
    if other in row[MaitriRelation.FRIEND]:
        return MaitriRelation.FRIEND
    if other in row[MaitriRelation.ENEMY]:
        return MaitriRelation.ENEMY
    return MaitriRelation.NEUTRAL


def get_mutual_maitri(first: Graha, second: Graha) -> MaitriRelation:
    """Combined relationship of a pair of rasi lords.

    Returns ``FRIEND`` when both are friends of each other (or the same
    graha rules both rasis); ``ENEMY`` when both are enemies; otherwise
    ``NEUTRAL``. This is the relationship used by the Rasi Athipathi
    porutham (docs/02 §7: "Mutually friends → Uthamam; one friendly /
    one neutral or both neutral → Madhyamam; mutually enemies →
    Athamam").
    """
    if first == second:
        return MaitriRelation.FRIEND
    first_toward_second = get_maitri_relation(first, second)
    second_toward_first = get_maitri_relation(second, first)
    if (
        first_toward_second is MaitriRelation.FRIEND
        and second_toward_first is MaitriRelation.FRIEND
    ):
        return MaitriRelation.FRIEND
    if first_toward_second is MaitriRelation.ENEMY and second_toward_first is MaitriRelation.ENEMY:
        return MaitriRelation.ENEMY
    return MaitriRelation.NEUTRAL
