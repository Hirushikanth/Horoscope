"""Integration tests: the yogatara stars endpoint (Phase E).

Covers ``POST /api/v2/stars`` payload contracts (catalogue size, star
fields, Thirukanitha badge), error propagation and OpenAPI rendering —
the M5 exit criteria for the stars surface.
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

STAR_FIELDS = {
    "hip_id",
    "name",
    "designation",
    "sanskrit_name",
    "associated_nakshatra_index",
    "associated_nakshatra",
    "magnitude",
    "ra_hours",
    "dec_degrees",
    "distance_light_years",
    "tropical_longitude_deg",
    "sidereal_longitude_deg",
    "ecliptic_latitude_deg",
    "rasi_index",
    "rasi",
    "nakshatra_index",
    "proper_motion_ra_mas_per_year",
    "proper_motion_dec_mas_per_year",
}


@pytest.fixture(scope="module")
def client() -> TestClient:
    """Module-scoped ASGI test client."""
    return TestClient(create_app())


class TestStarsEndpoint:
    def test_returns_full_catalog(self, client):
        response = client.post("/api/v2/stars", json=BIRTH)
        assert response.status_code == 200
        body = response.json()
        assert body["count"] == 36
        assert len(body["stars"]) == 36

    def test_every_star_has_full_contract(self, client):
        stars = client.post("/api/v2/stars", json=BIRTH).json()["stars"]
        for star in stars:
            assert set(star) == STAR_FIELDS
            assert star["hip_id"] > 0
            assert star["name"]
            assert 0.0 <= star["sidereal_longitude_deg"] < 360.0
            assert 0 <= star["rasi_index"] <= 11
            assert 0 <= star["nakshatra_index"] <= 26
            assert star["rasi"]["tamil"]

    def test_all_27_yogataras_have_nakshatra_associations(self, client):
        stars = client.post("/api/v2/stars", json=BIRTH).json()["stars"]
        associations = [
            star["associated_nakshatra_index"]
            for star in stars
            if star["associated_nakshatra_index"] is not None
        ]
        assert sorted(associations) == list(range(27))
        for star in stars:
            if star["associated_nakshatra_index"] is None:
                assert star["associated_nakshatra"] is None
            else:
                assert star["associated_nakshatra"]["english"]

    def test_chitra_anchor_is_exactly_180_sidereal(self, client):
        stars = client.post("/api/v2/stars", json=BIRTH).json()["stars"]
        chitra = next(star for star in stars if star["name"] == "Spica")
        assert chitra["sidereal_longitude_deg"] == pytest.approx(180.0, abs=1e-9)
        assert chitra["rasi_index"] == 6  # Libra
        assert chitra["associated_nakshatra"]["tamil"] == "Chithirai"

    def test_meta_badge_is_present(self, client):
        meta = client.post("/api/v2/stars", json=BIRTH).json()["meta"]
        assert meta["tradition"] == "Thirukanitham (Drik Ganita)"
        assert meta["precision"] == "IEEE 754 float64"
        assert meta["ayanamsa"]["system"] == "lahiri"

    def test_birth_echo_is_present(self, client):
        birth = client.post("/api/v2/stars", json=BIRTH).json()["birth"]
        assert birth["date"] == BIRTH["date"]
        assert birth["timezone"] == BIRTH["timezone"]
        assert "jd_ut1" in birth

    def test_stars_are_sorted_brightest_first(self, client):
        stars = client.post("/api/v2/stars", json=BIRTH).json()["stars"]
        magnitudes = [star["magnitude"] for star in stars]
        assert magnitudes == sorted(magnitudes)

    def test_response_is_deterministic_and_cacheable(self, client):
        first = client.post("/api/v2/stars", json=BIRTH)
        second = client.post("/api/v2/stars", json=BIRTH)
        assert first.status_code == 200
        assert first.json() == second.json()

    def test_response_has_no_numpy_leaks(self, client):
        response = client.post("/api/v2/stars", json=BIRTH)
        assert "numpy" not in response.text


class TestStarsValidation:
    def test_semantically_invalid_date_is_400(self, client):
        response = client.post("/api/v2/stars", json={**BIRTH, "date": "2023-02-30"})
        assert response.status_code == 400
        assert response.json()["detail"]["code"] == "invalid_birth_data"

    def test_out_of_range_date_is_422(self, client):
        response = client.post("/api/v2/stars", json={**BIRTH, "date": "1400-01-01"})
        assert response.status_code == 422
        assert response.json()["detail"]["code"] == "date_out_of_range"

    def test_unknown_timezone_is_422(self, client):
        response = client.post("/api/v2/stars", json={**BIRTH, "timezone": "Mars/Olympus"})
        assert response.status_code == 422

    def test_extra_fields_rejected(self, client):
        response = client.post("/api/v2/stars", json={**BIRTH, "surprise": 1})
        assert response.status_code == 422


class TestStarsOpenAPI:
    def test_openapi_documents_stars_path(self, client):
        spec = client.get("/openapi.json").json()
        assert "/api/v2/stars" in spec["paths"]
        assert "post" in spec["paths"]["/api/v2/stars"]

    def test_openapi_renders_clean(self, client):
        response = client.get("/docs")
        assert response.status_code == 200
        assert "swagger-ui" in response.text.lower()
