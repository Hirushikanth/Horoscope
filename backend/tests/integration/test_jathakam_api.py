"""Integration tests: jathakam computation endpoints (Phase C).

Covers the flagship ``POST /api/v2/jathakam`` and the focused
panchangam / dasha / vargas endpoints: payload contracts, error codes
and OpenAPI rendering (M3 exit criteria).
"""

from __future__ import annotations

import pytest
from app.main import create_app
from fastapi.testclient import TestClient

BIRTH: dict = {
    "date": "1990-06-15",
    "time": "06:30:00",
    "timezone": "Asia/Colombo",
    "latitude": 6.9271,
    "longitude": 79.8612,
}


@pytest.fixture(scope="module")
def client() -> TestClient:
    """Module-scoped ASGI test client."""
    return TestClient(create_app())


class TestJathakamEndpoint:
    def test_returns_full_payload(self, client):
        response = client.post("/api/v2/jathakam", json=BIRTH)
        assert response.status_code == 200
        body = response.json()
        assert len(body["grahas"]) == 9
        assert len(body["bhavas"]) == 12
        assert len(body["dasha"]["periods"]) >= 9
        assert "chevvai_dosham" in body

    def test_meta_badge_is_present(self, client):
        body = client.post("/api/v2/jathakam", json=BIRTH).json()
        meta = body["meta"]
        assert meta["tradition"] == "Thirukanitham (Drik Ganita)"
        assert meta["precision"] == "IEEE 754 float64"
        assert meta["ayanamsa"]["system"] == "lahiri"
        assert meta["ayanamsa"]["value_deg"] > 20.0
        assert meta["ephemeris"]["name"] == "de440.bsp"

    def test_panchangam_has_five_angas(self, client):
        panchangam = client.post("/api/v2/jathakam", json=BIRTH).json()["panchangam"]
        assert set(panchangam) == {"tithi", "vara", "nakshatra", "yoga", "karana"}
        nakshatra = panchangam["nakshatra"]
        assert 0 <= nakshatra["index"] <= 26
        assert 1 <= nakshatra["pada"] <= 4
        assert panchangam["tithi"]["paksha"] in ("shukla", "krishna")

    def test_lagna_and_grahas_are_consistent(self, client):
        body = client.post("/api/v2/jathakam", json=BIRTH).json()
        lagna_rasi = body["lagna"]["rasi_index"]
        assert 0 <= lagna_rasi <= 11
        for graha in body["grahas"]:
            assert 1 <= graha["house_number"] <= 12
            assert 0 <= graha["rasi_index"] <= 11
            assert 0 <= graha["navamsa_rasi_index"] <= 11
            assert graha["dignity"]["dignity"] in (
                "exalted",
                "debilitated",
                "moolatrikona",
                "own_sign",
                "neutral",
            )
            for field in ("sidereal_longitude_deg", "nakshatra_index", "pada"):
                assert field in graha

    def test_dasha_balance_reported(self, client):
        dasha = client.post("/api/v2/jathakam", json=BIRTH).json()["dasha"]
        balance = dasha["balance"]
        assert balance["lord"]
        assert 0.0 < balance["fraction_remaining"] <= 1.0
        assert balance["balance_days"] > 0.0
        for period in dasha["periods"]:
            assert period["category"] == "mahadasha"
            assert period["start_utc"] < period["end_utc"]

    def test_chevvai_dosham_structure(self, client):
        dosham = client.post("/api/v2/jathakam", json=BIRTH).json()["chevvai_dosham"]
        assert set(dosham) == {
            "present",
            "reference_count",
            "houses_from_lagna",
            "houses_from_moon",
            "houses_from_venus",
        }
        assert 0 <= dosham["reference_count"] <= 3

    def test_response_has_no_numpy_leaks(self, client):
        response = client.post("/api/v2/jathakam", json=BIRTH)
        assert "numpy" not in response.text


class TestPanchangamEndpoint:
    def test_returns_birth_panchangam(self, client):
        response = client.post("/api/v2/jathakam/panchangam", json=BIRTH)
        assert response.status_code == 200
        panchangam = response.json()["panchangam"]
        assert set(panchangam) == {"tithi", "vara", "nakshatra", "yoga", "karana"}

    def test_almanac_reports_day_windows(self, client):
        almanac = client.post("/api/v2/jathakam/panchangam", json=BIRTH).json()["almanac"]
        assert almanac["available"] is True
        assert almanac["sunrise_utc"] is not None
        assert almanac["sunset_utc"] is not None
        for window_name in ("rahu_kalam", "yamagandam", "gulika", "abhijit"):
            window = almanac[window_name]
            assert window is not None
            assert window["start_local"] < window["end_local"]

    def test_almanac_windows_are_within_sunrise_sunset(self, client):
        from datetime import datetime

        almanac = client.post("/api/v2/jathakam/panchangam", json=BIRTH).json()["almanac"]
        sunrise = datetime.fromisoformat(almanac["sunrise_utc"])
        sunset = datetime.fromisoformat(almanac["sunset_utc"])
        # Some segments (e.g. Friday Gulika) start exactly at sunrise.
        for window_name in ("rahu_kalam", "yamagandam", "gulika"):
            window = almanac[window_name]
            start = datetime.fromisoformat(window["start_utc"])
            end = datetime.fromisoformat(window["end_utc"])
            assert sunrise <= start < end <= sunset


class TestDashaEndpoint:
    def test_depth_one_returns_mahadashas(self, client):
        body = client.post("/api/v2/jathakam/dasha", json={**BIRTH, "depth": 1}).json()["dasha"]
        assert body["periods"]
        assert {p["category"] for p in body["periods"]} == {"mahadasha"}

    def test_depth_three_returns_all_categories(self, client):
        body = client.post("/api/v2/jathakam/dasha", json={**BIRTH, "depth": 3}).json()["dasha"]
        categories = {p["category"] for p in body["periods"]}
        assert categories == {"mahadasha", "antardasha", "pratyantardasha"}
        assert len(body["periods"]) == 10 + 90 + 810

    def test_year_length_switch_changes_day_counts(self, client):
        modern = client.post(
            "/api/v2/jathakam/dasha", json={**BIRTH, "depth": 1, "year_length_days": 365.25}
        ).json()["dasha"]
        tamil = client.post(
            "/api/v2/jathakam/dasha", json={**BIRTH, "depth": 1, "year_length_days": 360.0}
        ).json()["dasha"]
        assert modern["year_length_days"] == 365.25
        assert tamil["year_length_days"] == 360.0
        assert tamil["balance"]["balance_days"] < modern["balance"]["balance_days"]

    def test_antardashas_span_their_mahadasha(self, client):
        periods = client.post("/api/v2/jathakam/dasha", json={**BIRTH, "depth": 2}).json()["dasha"][
            "periods"
        ]
        mahadashas = [p for p in periods if p["category"] == "mahadasha"]
        antardashas = [p for p in periods if p["category"] == "antardasha"]
        assert len(antardashas) == 9 * len(mahadashas)
        assert antardashas[0]["start_jd"] == mahadashas[0]["start_jd"]
        assert antardashas[-1]["end_jd"] == pytest.approx(mahadashas[-1]["end_jd"], rel=1e-9)


class TestVargasEndpoint:
    def test_defaults_to_navamsa(self, client):
        body = client.post("/api/v2/jathakam/vargas", json=BIRTH).json()
        assert len(body["grahas"]) == 9
        for graha in body["grahas"]:
            assert set(graha["positions"]) == {"D9"}
            assert "rasi_index" in graha["positions"]["D9"]

    def test_requests_multiple_vargas(self, client):
        body = client.post(
            "/api/v2/jathakam/vargas", json={**BIRTH, "vargas": ["D1", "D9", "D60"]}
        ).json()
        for graha in body["grahas"]:
            assert set(graha["positions"]) == {"D1", "D9", "D60"}
            assert graha["positions"]["D1"]["rasi_index"] == graha["positions"]["D1"]["rasi_index"]

    def test_d1_matches_jathakam_rasi(self, client):
        jathakam = client.post("/api/v2/jathakam", json=BIRTH).json()["grahas"]
        vargas = client.post("/api/v2/jathakam/vargas", json={**BIRTH, "vargas": ["D1"]}).json()[
            "grahas"
        ]
        by_name = {g["name"]: g for g in jathakam}
        for graha in vargas:
            assert graha["positions"]["D1"]["rasi_index"] == by_name[graha["name"]]["rasi_index"]


class TestValidation:
    def test_semantically_invalid_date_is_400(self, client):
        response = client.post("/api/v2/jathakam", json={**BIRTH, "date": "2023-02-30"})
        assert response.status_code == 400
        assert response.json()["detail"]["code"] == "invalid_birth_data"

    def test_out_of_range_date_is_422(self, client):
        response = client.post("/api/v2/jathakam", json={**BIRTH, "date": "1400-01-01"})
        assert response.status_code == 422
        assert response.json()["detail"]["code"] == "date_out_of_range"

    def test_unknown_timezone_is_422(self, client):
        response = client.post("/api/v2/jathakam", json={**BIRTH, "timezone": "Mars/Olympus"})
        assert response.status_code == 422

    def test_latitude_out_of_bounds_is_422(self, client):
        response = client.post("/api/v2/jathakam", json={**BIRTH, "latitude": 91.0})
        assert response.status_code == 422

    def test_malformed_date_format_is_422(self, client):
        response = client.post("/api/v2/jathakam", json={**BIRTH, "date": "15-06-1990"})
        assert response.status_code == 422

    def test_extra_fields_rejected(self, client):
        response = client.post("/api/v2/jathakam", json={**BIRTH, "surprise": 1})
        assert response.status_code == 422

    def test_unsupported_varga_is_422(self, client):
        response = client.post("/api/v2/jathakam/vargas", json={**BIRTH, "vargas": ["D7"]})
        assert response.status_code == 422

    def test_duplicate_vargas_rejected(self, client):
        response = client.post("/api/v2/jathakam/vargas", json={**BIRTH, "vargas": ["D9", "D9"]})
        assert response.status_code == 422

    def test_unsupported_year_length_rejected(self, client):
        response = client.post("/api/v2/jathakam/dasha", json={**BIRTH, "year_length_days": 361.0})
        assert response.status_code == 422


class TestOpenAPI:
    def test_openapi_documents_jathakam_paths(self, client):
        spec = client.get("/openapi.json").json()
        paths = spec["paths"]
        for path in (
            "/api/v2/jathakam",
            "/api/v2/jathakam/panchangam",
            "/api/v2/jathakam/dasha",
            "/api/v2/jathakam/vargas",
        ):
            assert path in paths, f"{path} missing from OpenAPI"
            assert "post" in paths[path]

    def test_openapi_renders_clean(self, client):
        response = client.get("/docs")
        assert response.status_code == 200
        assert "swagger-ui" in response.text.lower()
