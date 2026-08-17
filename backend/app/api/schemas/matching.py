"""
matching.py — Pydantic v2 response contract for the Kalyana Porutham
matching endpoint.

The response is self-documenting like every v2 endpoint (``meta``
badge), carries the bride/groom jathakam briefs, all eleven porutham
checks (ten scored + nadi), the 10-point score, the verdict with its
gate/non-negotiable reasons, and the Chevvai Dosham cross-check.

References:
    - docs/backend-v2-plan.md §2 (API surface, trust feature)
    - docs/02-kalyana-porutham-matching.md (all porutham rules)
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict

from app.api.schemas.jathakam import BirthInfo, ComputationBadge, Trilingual


class PartnerBrief(BaseModel):
    """The matching-relevant extract of one partner's jathakam.

    References:
        docs/02-kalyana-porutham-matching.md, §0 (what you need)
    """

    birth: BirthInfo
    nakshatra_index: int  # 0-based (0–26)
    pada: int  # 1-based (1–4)
    nakshatra: Trilingual
    rasi_index: int  # 0-based (0–11)
    rasi: Trilingual
    moon_degree_in_sign_deg: float
    chevvai_dosham: bool


class PoruthamCheck(BaseModel):
    """One of the eleven porutham checks with its outcome."""

    id: str  # e.g. "dina"
    name: Trilingual
    governs: str
    result: str  # "uthamam" | "madhyamam" | "athamam"
    score: float  # 1.0 / 0.5 / 0.0 (0.0 for nadi, which is not scored)
    in_total: bool  # False only for nadi (the "+" eleventh check)
    detail: dict  # rule-specific values (counts, groups, lords, flags)
    notes: list[str]  # exceptions or judgement calls applied


class MatchingScore(BaseModel):
    """The 10-point score summary (nadi excluded)."""

    total: float
    out_of: int  # always 10
    uthamam_count: int
    madhyamam_count: int
    athamam_count: int


class MatchingVerdict(BaseModel):
    """The overall verdict with every override explained.

    References:
        docs/02-kalyana-porutham-matching.md — "Overall scoring and
        interpretation" (bands, gates, non-negotiables).
    """

    verdict: str  # "uthamam" | "madhyamam" | "athamam"
    band: str  # "8–10" | "6–7" | "≤5"
    gates: dict[str, str]  # rajju/vedha → "ok" | "failed"
    non_negotiables: dict[str, bool]  # dina/gana/yoni/rasi/rajju
    gate_overridden: bool  # gate failure forced a downgrade from 8–10
    reasons: list[str]


class ChevvaiCrossCheck(BaseModel):
    """Chevvai Dosham cross-check — a separate condition, not scored.

    References:
        docs/02-kalyana-porutham-matching.md — "Cross-check: Chevvai
        Dosham" section.
    """

    bride_dosham: bool
    groom_dosham: bool
    compatible: bool  # both share the same status
    note: str


class MatchingResponse(BaseModel):
    """Kalyana Porutham — eleven checks, scoring and verdict."""

    model_config = ConfigDict(extra="ignore")

    meta: ComputationBadge
    tradition: str
    bride: PartnerBrief
    groom: PartnerBrief
    poruthams: list[PoruthamCheck]
    score: MatchingScore
    verdict: MatchingVerdict
    chevvai_cross_check: ChevvaiCrossCheck
