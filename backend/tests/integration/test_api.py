"""Integration tests: API surface, error contract, headers."""

from __future__ import annotations

import pytest
from app.main import create_app
from fastapi.testclient import TestClient


@pytest.fixture(scope="module")
def client() -> TestClient:
    """Module-scoped ASGI test client."""
    return TestClient(create_app())


class TestHealth:
    def test_health_reports_ok(self, client):
        response = client.get("/api/v2/health")
        assert response.status_code == 200
        body = response.json()
        assert body["status"] == "ok"
        assert body["version"] == "2.0.0"
        assert body["ephemeris"]["name"] == "de440.bsp"

    def test_health_reports_availability_without_loading(self, client):

        response = client.get("/api/v2/health")
        assert response.status_code == 200
        assert "loaded" in response.json()["ephemeris"]


class TestMeta:
    def test_meta_reports_precision_and_tradition(self, client):
        response = client.get("/api/v2/meta")
        assert response.status_code == 200
        body = response.json()
        assert body["precision"] == "IEEE 754 float64"
        assert body["tradition"] == "Thirukanitham (Drik Ganita)"
        assert body["ephemeris"]["source"] == "NASA JPL DE440"
        assert body["ayanamsa"]["system"] == "lahiri"
        assert 20.0 < body["ayanamsa"]["value_deg"] < 30.0

    def test_meta_returns_request_id(self, client):
        response = client.get("/api/v2/meta", headers={"X-Request-ID": "corr-123"})
        assert response.status_code == 200
        assert response.headers.get("X-Request-ID") == "corr-123"

    def test_meta_generates_request_id_when_absent(self, client):
        response = client.get("/api/v2/meta")
        assert response.status_code == 200
        assert response.headers.get("X-Request-ID")


class TestErrorContract:
    def test_unknown_route_is_404(self, client):
        response = client.get("/api/v2/does-not-exist")
        assert response.status_code == 404

    def test_no_internal_leaks(self, client):
        response = client.get("/api/v2/meta")
        assert "traceback" not in response.text.lower()

    def test_validation_error_has_typed_contract(self, client):
        response = client.post("/api/v2/jathakam", json={"date": "not-a-date"})
        assert response.status_code == 422
        detail = response.json()["detail"]
        assert detail["code"] == "validation_error"
        assert detail["message"]
        assert isinstance(detail["context"]["fields"], list)
        assert detail["context"]["fields"]

    def test_validation_error_lists_offending_fields(self, client):
        response = client.post(
            "/api/v2/jathakam",
            json={"date": "bad", "time": "bad", "timezone": "", "latitude": 999, "longitude": 0},
        )
        detail = response.json()["detail"]
        field_locs = {field["loc"][-1] for field in detail["context"]["fields"]}
        assert {"date", "time", "timezone", "latitude"} <= field_locs
