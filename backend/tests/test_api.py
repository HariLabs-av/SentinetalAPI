from fastapi.testclient import TestClient

from sentinelapi.main import app


def test_health_contract():
    response = TestClient(app).get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_discovery_rejects_non_http_target():
    response = TestClient(app).post("/api/v1/discover", json={"target_url": "file:///tmp/x"})
    assert response.status_code == 422


def test_ai_report_requires_configuration():
    response = TestClient(app).post("/api/v1/scan/unknown/ai-report")
    assert response.status_code == 404
