"""matching — the Kalyana Porutham engine (docs/02)."""

from app.matching.poruthams import (
    ALL_PORUTHAMS,
    PORUTHAM_GOVERNS,
    PORUTHAM_NAMES,
    MatchingInput,
    PoruthamReport,
    PoruthamResult,
    compute_all_poruthams,
)
from app.matching.scoring import (
    GATE_PORUTHAMS,
    NON_NEGOTIABLE_PORUTHAMS,
    SCORED_PORUTHAMS,
    ScoreReport,
    Verdict,
    VerdictReport,
    assess_verdict,
    score_reports,
)

__all__ = [
    "ALL_PORUTHAMS",
    "GATE_PORUTHAMS",
    "NON_NEGOTIABLE_PORUTHAMS",
    "PORUTHAM_GOVERNS",
    "PORUTHAM_NAMES",
    "SCORED_PORUTHAMS",
    "MatchingInput",
    "PoruthamReport",
    "PoruthamResult",
    "ScoreReport",
    "Verdict",
    "VerdictReport",
    "assess_verdict",
    "compute_all_poruthams",
    "score_reports",
]
