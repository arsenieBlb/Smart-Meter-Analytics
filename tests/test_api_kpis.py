from __future__ import annotations

from fastapi.testclient import TestClient

from api.database import get_db
from api.main import app


def override_db() -> None:
    return None


def test_api_root_endpoint_works() -> None:
    app.dependency_overrides[get_db] = override_db
    client = TestClient(app)

    response = client.get("/")

    app.dependency_overrides.clear()
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_kpi_endpoint_returns_required_fields() -> None:
    app.dependency_overrides[get_db] = override_db
    client = TestClient(app)

    response = client.get("/api/kpis")

    app.dependency_overrides.clear()
    assert response.status_code == 200
    payload = response.json()
    assert {
        "total_consumption",
        "active_meters",
        "reading_success_rate",
        "missing_reading_percentage",
        "anomaly_count",
        "critical_meter_count",
        "latest_reading_timestamp",
    }.issubset(payload)

