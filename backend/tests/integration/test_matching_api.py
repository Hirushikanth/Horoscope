"""Integration tests: the Kalyana Porutham matching endpoint (Phase D).

Covers ``POST /api/v2/matching``: payload contract, internal
consistency between the response and the pure porutham functions,
bride→groom directionality, error handling and OpenAPI rendering
(M4 exit criteria: correct verdicts, gate logic, clean docs).
"""

from __future__ import annotations

import numpy as np
import pytest
from app.main import create_app
from app.matching.poruthams import (
    MatchingInput,
    compute_all_poruthams,
)
from fastapi.testclient import TestClient

BRIDE: dict = {
    "date": "1990-06-15",
    "time": "06:30:00",
    "timezone": "Asia/Colombo",
    "latitude": 6.9271,
    "longitude": 79.8612,
}
GROOM: dict = {
    "date": "1988-11-02",
    "time": "14:15:00",
    "timezone": "Asia/Kolkata",
    "latitude": 13.0827,
    "longitude": 80.2707,
}


@pytest.fixture(scope="module")
def client() -> TestClient:
    """Module-scoped ASGI test client."""
    return TestClient(create_app())


class TestMatchingEndpoint:
    def test_returns_full_payload(self, client):
        response = client.post("/api/v2/matching", json={"bride": BRIDE, "groom": GROOM})
        assert response.status_code == 200
        body = response.json()
        assert body["tradition"] == "Kalyana Porutham (Tamil convention)"
        assert len(body["poruthams"]) == 11
        assert body["score"]["out_of"] == 10
        assert set(body["verdict"]) == {
            "verdict",
            "band",
            "gates",
            "non_negotiables",
            "gate_overridden",
            "reasons",
        }
        assert set(body["chevvai_cross_check"]) == {
            "bride_dosham",
            "groom_dosham",
            "compatible",
            "note",
        }

    def test_meta_badge_is_present(self, client):
        body = client.post("/api/v2/matching", json={"bride": BRIDE, "groom": GROOM}).json()
        meta = body["meta"]
        assert meta["tradition"] == "Thirukanitham (Drik Ganita)"
        assert meta["precision"] == "IEEE 754 float64"
        assert meta["ayanamsa"]["system"] == "lahiri"

    def test_porutham_checks_are_in_traditional_order(self, client):
        body = client.post("/api/v2/matching", json={"bride": BRIDE, "groom": GROOM}).json()
        ids = [p["id"] for p in body["poruthams"]]
        assert ids == [
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
            "nadi",
        ]
        assert body["poruthams"][-1]["in_total"] is False  # nadi

    def test_each_porutham_has_full_contract(self, client):
        body = client.post("/api/v2/matching", json={"bride": BRIDE, "groom": GROOM}).json()
        for porutham in body["poruthams"]:
            assert porutham["result"] in ("uthamam", "madhyamam", "athamam")
            assert porutham["score"] in (1.0, 0.5, 0.0)
            assert porutham["name"]["english"]
            assert porutham["governs"]
            assert isinstance(porutham["detail"], dict)
            assert isinstance(porutham["notes"], list)

    def test_score_matches_recomputation(self, client):
        """The endpoint's score equals the pure scoring of the reported
        porutham results — the service pipeline is internally consistent."""
        body = client.post("/api/v2/matching", json={"bride": BRIDE, "groom": GROOM}).json()
        recomputed = sum(p["score"] for p in body["poruthams"] if p["in_total"])
        assert body["score"]["total"] == pytest.approx(recomputed)

    def test_response_matches_pure_functions(self, client):
        """Every porutham in the response equals the pure-domain result
        computed from the bride/groom briefs — no service-layer drift."""
        body = client.post("/api/v2/matching", json={"bride": BRIDE, "groom": GROOM}).json()
        bride_input = MatchingInput(
            nakshatra_index=body["bride"]["nakshatra_index"],
            pada=body["bride"]["pada"],
            rasi_index=body["bride"]["rasi_index"],
            moon_degree_in_sign=np.float64(body["bride"]["moon_degree_in_sign_deg"]),
            chevvai_dosham=body["bride"]["chevvai_dosham"],
        )
        groom_input = MatchingInput(
            nakshatra_index=body["groom"]["nakshatra_index"],
            pada=body["groom"]["pada"],
            rasi_index=body["groom"]["rasi_index"],
            moon_degree_in_sign=np.float64(body["groom"]["moon_degree_in_sign_deg"]),
            chevvai_dosham=body["groom"]["chevvai_dosham"],
        )
        expected = compute_all_poruthams(bride_input, groom_input)
        for porutham in body["poruthams"]:
            pure = expected[porutham["id"]]
            assert porutham["result"] == pure.result.value, porutham["id"]
            assert porutham["detail"] == pure.detail, porutham["id"]
            assert porutham["notes"] == list(pure.notes), porutham["id"]

    def test_brief_reports_partner_data(self, client):
        body = client.post("/api/v2/matching", json={"bride": BRIDE, "groom": GROOM}).json()
        for partner in ("bride", "groom"):
            brief = body[partner]
            assert 0 <= brief["nakshatra_index"] <= 26
            assert 1 <= brief["pada"] <= 4
            assert 0 <= brief["rasi_index"] <= 11
            assert 0.0 <= brief["moon_degree_in_sign_deg"] < 30.0
            assert brief["birth"]["date"]

    def test_swapping_partners_changes_result(self, client):
        """Counting is bride→groom; a swapped pair must produce a
        different score where checks are directional."""
        body = client.post("/api/v2/matching", json={"bride": BRIDE, "groom": GROOM}).json()
        swapped = client.post("/api/v2/matching", json={"bride": GROOM, "groom": BRIDE}).json()
        assert body["score"]["total"] != swapped["score"]["total"]
        # The dina count must mirror across the swap: count is the
        # inclusive step from bride to groom, so reversing partners
        # yields ((28 - count) % 27) + 1.
        count = body["poruthams"][0]["detail"]["count"]
        swapped_count = swapped["poruthams"][0]["detail"]["count"]
        assert swapped_count == ((28 - count) % 27) + 1

    def test_determinism(self, client):
        first = client.post("/api/v2/matching", json={"bride": BRIDE, "groom": GROOM})
        second = client.post("/api/v2/matching", json={"bride": BRIDE, "groom": GROOM})
        assert first.text == second.text

    def test_no_numpy_leaks(self, client):
        response = client.post("/api/v2/matching", json={"bride": BRIDE, "groom": GROOM})
        assert "numpy" not in response.text


class TestMatchingValidation:
    def test_missing_groom_is_422(self, client):
        response = client.post("/api/v2/matching", json={"bride": BRIDE})
        assert response.status_code == 422

    def test_malformed_birth_is_422(self, client):
        response = client.post(
            "/api/v2/matching",
            json={"bride": {**BRIDE, "time": "not-a-time"}, "groom": GROOM},
        )
        assert response.status_code == 422

    def test_semantically_invalid_date_is_400(self, client):
        response = client.post(
            "/api/v2/matching",
            json={"bride": {**BRIDE, "date": "2023-02-30"}, "groom": GROOM},
        )
        assert response.status_code == 400
        assert response.json()["detail"]["code"] == "invalid_birth_data"

    def test_extra_top_level_fields_rejected(self, client):
        response = client.post(
            "/api/v2/matching", json={"bride": BRIDE, "groom": GROOM, "system": "ashtakoot"}
        )
        assert response.status_code == 422


class TestMatchingOpenAPI:
    def test_openapi_documents_matching_path(self, client):
        spec = client.get("/openapi.json").json()
        assert "/api/v2/matching" in spec["paths"]
        assert "post" in spec["paths"]["/api/v2/matching"]

    def test_openapi_renders_clean(self, client):
        response = client.get("/docs")
        assert response.status_code == 200
        assert "swagger-ui" in response.text.lower()
