"""Verify the public health contract and API registration."""

from fastapi.testclient import TestClient

from app.main import app


def test_health_returns_service_identity() -> None:
    # The context manager runs application startup and shutdown.
    with TestClient(app) as client:
        response = client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/json"
    assert response.json() == {"status": "ok", "service": "digitalent-ai"}


def test_health_has_one_versioned_get_operation() -> None:
    with TestClient(app) as client:
        schema = client.get("/openapi.json").json()
        assert client.get("/health").status_code == 404
        assert client.get("/api/api/v1/health").status_code == 404
        assert client.post("/api/v1/health").status_code == 405

    assert set(schema["paths"]) == {"/api/v1/health", "/api/v1/health/db"}
    assert list(schema["paths"]["/api/v1/health"]) == ["get"]
