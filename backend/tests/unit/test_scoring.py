"""Unit tests for porutham scoring and the overall verdict (Phase D, M4).

Covers the docs/02 scoring section: Uthamam=1 / Madhyamam=½ / Athamam=0,
the 8–10 / 6–7 / ≤5 verdict bands, the five non-negotiable poruthams
required for the 6–7 band, and the Rajju/Vedha pass-fail gates that
override high totals.
"""

from __future__ import annotations

import pytest
from app.matching.poruthams import PoruthamReport, PoruthamResult
from app.matching.scoring import (
    SCORED_PORUTHAMS,
    Verdict,
    assess_verdict,
    score_reports,
)


def _report(porutham_id: str, result: PoruthamResult) -> PoruthamReport:
    return PoruthamReport(
        id=porutham_id,
        result=result,
        in_total=porutham_id != "nadi",
        detail={},
    )


def _reports(
    *,
    uthamam: list[str] | None = None,
    madhyamam: list[str] | None = None,
    athamam: list[str] | None = None,
    nadi: PoruthamResult = PoruthamResult.UTHAMAM,
) -> dict[str, PoruthamReport]:
    """Build a full 11-check report set with the given distributions."""
    results = {pid: PoruthamResult.UTHAMAM for pid in SCORED_PORUTHAMS}
    for pid in madhyamam or []:
        results[pid] = PoruthamResult.MADHYAMAM
    for pid in athamam or []:
        results[pid] = PoruthamResult.ATHAMAM
    if uthamam is not None:
        for pid in SCORED_PORUTHAMS:
            results[pid] = PoruthamResult.UTHAMAM if pid in uthamam else PoruthamResult.ATHAMAM
    results["nadi"] = nadi
    return {pid: _report(pid, result) for pid, result in results.items()}


# ═══════════════════════════════════════════════════════════════════════ #
# Scoring
# ═══════════════════════════════════════════════════════════════════════ #


def test_score_all_uthamam_is_ten() -> None:
    score = score_reports(_reports())
    assert score.total == pytest.approx(10.0)
    assert score.out_of == 10
    assert score.uthamam_count == 10


def test_score_athamam_counts_zero() -> None:
    score = score_reports(_reports(athamam=list(SCORED_PORUTHAMS)))
    assert score.total == pytest.approx(0.0)
    assert score.athamam_count == 10


def test_score_madhyamam_halves() -> None:
    score = score_reports(_reports(madhyamam=["dina", "yoni", "vashya"]))
    assert score.total == pytest.approx(8.5)
    assert score.madhyamam_count == 3
    assert score.uthamam_count == 7


def test_score_mixed_distribution() -> None:
    score = score_reports(_reports(uthamam=["dina", "gana", "yoni", "rasi"], madhyamam=[]))
    # 4 uthamam + 6 athamam = 4.0
    assert score.total == pytest.approx(4.0)
    assert score.athamam_count == 6


def test_score_excludes_nadi() -> None:
    # Nadi Athamam must not change a perfect 10.
    score = score_reports(_reports(nadi=PoruthamResult.ATHAMAM))
    assert score.total == pytest.approx(10.0)


def test_score_requires_all_ten() -> None:
    reports = _reports()
    del reports["rajju"]
    with pytest.raises(ValueError, match="rajju"):
        score_reports(reports)


# ═══════════════════════════════════════════════════════════════════════ #
# Verdict bands
# ═══════════════════════════════════════════════════════════════════════ #


def test_verdict_perfect_match_is_uthamam() -> None:
    verdict = assess_verdict(_reports())
    assert verdict.verdict is Verdict.UTHAMAM
    assert verdict.band == "8–10"


def test_verdict_eight_is_uthamam() -> None:
    # Two Madhyamam checks on a clean chart → 9.0.
    verdict = assess_verdict(_reports(madhyamam=["mahendra", "stree_deergha"]))
    assert verdict.verdict is Verdict.UTHAMAM


def test_verdict_seven_with_non_negotiables_is_madhyamam() -> None:
    # 6 Uthamam + 1 Madhyamam + 3 Athamam = 6.5, non-negotiables clean.
    verdict = assess_verdict(_reports(athamam=["mahendra", "stree_deergha", "vashya"]))
    assert verdict.verdict is Verdict.MADHYAMAM
    assert verdict.band == "6–7"


def test_verdict_six_and_a_half_is_madhyamam() -> None:
    verdict = assess_verdict(
        _reports(athamam=["mahendra", "stree_deergha", "vashya", "rasi_athipathi"])
    )
    assert verdict.verdict is Verdict.MADHYAMAM


def test_verdict_six_band_missing_non_negotiable_is_athamam() -> None:
    # 6.5 total but dina is Athamam → the 6–7 band is not awarded.
    verdict = assess_verdict(_reports(athamam=["dina", "mahendra", "stree_deergha", "vashya"]))
    assert verdict.verdict is Verdict.ATHAMAM
    assert verdict.non_negotiables["dina"] is False
    assert "non-negotiable" in verdict.reasons[0]


def test_verdict_five_is_athamam() -> None:
    verdict = assess_verdict(_reports(uthamam=["dina", "gana", "yoni", "rasi", "rajju"]))
    assert verdict.verdict is Verdict.ATHAMAM
    assert verdict.band == "≤5"


# ═══════════════════════════════════════════════════════════════════════ #
# Gates — Rajju and Vedha override high totals
# ═══════════════════════════════════════════════════════════════════════ #


def test_verdict_rajju_gate_downgrades_ten() -> None:
    """A perfect 10 with Rajju Dosham must not be Uthamam."""
    verdict = assess_verdict(_reports(athamam=["rajju"]))
    assert verdict.verdict is Verdict.MADHYAMAM
    assert verdict.gate_overridden is True
    assert verdict.gates["rajju"] == "failed"
    assert verdict.gates["vedha"] == "ok"


def test_verdict_vedha_gate_downgrades_ten() -> None:
    verdict = assess_verdict(_reports(athamam=["vedha"]))
    assert verdict.verdict is Verdict.MADHYAMAM
    assert verdict.gate_overridden is True
    assert verdict.gates["vedha"] == "failed"


def test_verdict_both_gates_fail_downgrade() -> None:
    verdict = assess_verdict(_reports(athamam=["rajju", "vedha"]))
    assert verdict.verdict is Verdict.MADHYAMAM
    assert verdict.gates["rajju"] == "failed"
    assert verdict.gates["vedha"] == "failed"


def test_verdict_gate_cap_also_applies_at_eight() -> None:
    # 9.0 total, rajju Athamam → Madhyamam, not Uthamam.
    verdict = assess_verdict(_reports(athamam=["rajju"], madhyamam=["mahendra"]))
    assert verdict.verdict is Verdict.MADHYAMAM


def test_verdict_gates_ok_at_ten() -> None:
    verdict = assess_verdict(_reports())
    assert verdict.gates["rajju"] == "ok"
    assert verdict.gates["vedha"] == "ok"
    assert verdict.gate_overridden is False


def test_verdict_rajju_missing_lowers_6_7_band_to_athamam() -> None:
    """Rajju is also a non-negotiable — its absence fails the 6–7 band."""
    verdict = assess_verdict(_reports(athamam=["rajju", "mahendra", "stree_deergha", "vashya"]))
    assert verdict.verdict is Verdict.ATHAMAM
