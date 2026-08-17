"""
scoring.py — Kalyana Porutham scoring and overall verdict.

Each porutham scores Uthamam = 1, Madhyamam = ½, Athamam = 0, giving a
total out of 10 (nadi is the traditional "+" eleventh check and is
reported but excluded from the total). The verdict bands are 8–10
Uthamam, 6–7 Madhyamam and ≤5 Athamam, with two overrides faithful to
docs/02:

* **Gates** — Rajju (Rajju Dosham) and Vedha are pass/fail conditions,
  not points to be averaged away. A high total carrying either affliction
  is downgraded to Madhyamam.
* **Non-negotiables** — the 6–7 Madhyamam band is acceptable only when
  it includes Dina, Gana, Yoni, Rasi and Rajju; otherwise it falls to
  Athamam.

References:
    docs/02-kalyana-porutham-matching.md — "Overall scoring and
    interpretation" section.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from enum import StrEnum

import numpy as np

from app.matching.poruthams import PoruthamReport, PoruthamResult

#: The five poruthams required for the 6–7 Madhyamam band — docs/02.
NON_NEGOTIABLE_PORUTHAMS: tuple[str, ...] = ("dina", "gana", "yoni", "rasi", "rajju")

#: The pass/fail gates — docs/02 treats these as conditions.
GATE_PORUTHAMS: tuple[str, ...] = ("rajju", "vedha")

#: The ten poruthams counted in the total out of 10.
SCORED_PORUTHAMS: tuple[str, ...] = (
    "dina",
    "gana",
    "mahendra",
    "stree_deergha",
    "yoni",
    "rasi",
    "rasi_athipathi",
    "vashya",
    "rajju",
    "vedha",
)


class Verdict(StrEnum):
    """The overall match verdict — docs/02 scoring bands."""

    UTHAMAM = "uthamam"
    MADHYAMAM = "madhyamam"
    ATHAMAM = "athamam"


@dataclass(frozen=True)
class ScoreReport:
    """The 10-point score summary of a pair.

    Attributes:
        total: Sum of the ten scored poruthams (Uthamam 1, Madhyamam ½,
            Athamam 0), out of ``out_of``.
        out_of: Always 10 — nadi is reported but not scored.
        uthamam_count / madhyamam_count / athamam_count: Counts among
            the ten scored poruthams.
    """

    total: np.float64
    out_of: int = 10
    uthamam_count: int = 0
    madhyamam_count: int = 0
    athamam_count: int = 0


@dataclass(frozen=True)
class VerdictReport:
    """The overall verdict with every override explained.

    Attributes:
        verdict: The final Uthamam/Madhyamam/Athamam verdict.
        band: The raw score band (``"8–10"``, ``"6–7"`` or ``"≤5"``)
            before gate/non-negotiable overrides.
        gates: Per gate porutham, ``"ok"`` or ``"failed"``.
        non_negotiables: Per non-negotiable porutham, True when it is
            not Athamam.
        gate_overridden: True when a Rajju/Vedha gate forced a
            downgrade from the 8–10 band.
        reasons: Human-readable reasons for the final verdict.
    """

    verdict: Verdict
    band: str
    gates: dict[str, str] = field(default_factory=dict)
    non_negotiables: dict[str, bool] = field(default_factory=dict)
    gate_overridden: bool = False
    reasons: list[str] = field(default_factory=list)


def score_reports(reports: Mapping[str, PoruthamReport]) -> ScoreReport:
    """Score a set of porutham reports out of 10 (nadi excluded).

    Raises:
        ValueError: When any scored porutham is missing from ``reports``.
    """
    missing = [pid for pid in SCORED_PORUTHAMS if pid not in reports]
    if missing:
        raise ValueError(f"missing scored poruthams: {missing}")

    total = np.float64(0.0)
    uthamam = madhyamam = athamam = 0
    for pid in SCORED_PORUTHAMS:
        result = reports[pid].result
        total += result.score
        if result is PoruthamResult.UTHAMAM:
            uthamam += 1
        elif result is PoruthamResult.MADHYAMAM:
            madhyamam += 1
        else:
            athamam += 1

    return ScoreReport(
        total=total,
        uthamam_count=uthamam,
        madhyamam_count=madhyamam,
        athamam_count=athamam,
    )


def assess_verdict(reports: Mapping[str, PoruthamReport]) -> VerdictReport:
    """Combine the porutham reports into the overall verdict.

    Bands from the /10 total, then the two overrides from docs/02:

    1. A Rajju or Vedha affliction (gate failure) downgrades an 8–10
       total to Madhyamam — these are pass/fail, not points.
    2. The 6–7 band is Madhyamam only when all five non-negotiable
       poruthams are present; otherwise Athamam.
    """
    score = score_reports(reports)
    total = score.total

    gates = {
        pid: ("failed" if reports[pid].result is PoruthamResult.ATHAMAM else "ok")
        for pid in GATE_PORUTHAMS
    }
    non_negotiables = {
        pid: reports[pid].result is not PoruthamResult.ATHAMAM for pid in NON_NEGOTIABLE_PORUTHAMS
    }
    gate_failed = any(status == "failed" for status in gates.values())
    all_non_negotiables_ok = all(non_negotiables.values())
    reasons: list[str] = []

    if total >= np.float64(8.0):
        band = "8–10"
        if gate_failed:
            verdict = Verdict.MADHYAMAM
            reasons.append(
                "Total of 8–10 but a pass/fail gate failed (Rajju and/or "
                "Vedha) — the docs treat these as conditions, so the verdict "
                "is downgraded to Madhyamam."
            )
        else:
            verdict = Verdict.UTHAMAM
            reasons.append("Excellent match — total in the 8–10 Uthamam band.")
    elif total >= np.float64(6.0):
        band = "6–7"
        if all_non_negotiables_ok:
            verdict = Verdict.MADHYAMAM
            reasons.append(
                "Acceptable match — total in the 6–7 Madhyamam band with all "
                "five non-negotiable poruthams (Dina, Gana, Yoni, Rasi, Rajju)."
            )
        else:
            verdict = Verdict.ATHAMAM
            missing = [pid for pid, ok in non_negotiables.items() if not ok]
            reasons.append(
                "Total in the 6–7 band but missing non-negotiable poruthams "
                f"({', '.join(missing)}) — the Madhyamam verdict is not awarded."
            )
    else:
        band = "≤5"
        verdict = Verdict.ATHAMAM
        reasons.append("Not recommended — total of 5 or below (Athamam band).")

    return VerdictReport(
        verdict=verdict,
        band=band,
        gates=gates,
        non_negotiables=non_negotiables,
        gate_overridden=gate_failed,
        reasons=reasons,
    )
