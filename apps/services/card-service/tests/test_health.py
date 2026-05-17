from fastapi.testclient import TestClient

from app.main import SERVICE_NAME, app


client = TestClient(app)


def test_healthcheck_returns_service_name() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["service"] == SERVICE_NAME


def test_context_lists_planned_routes() -> None:
    response = client.get("/context")

    assert response.status_code == 200
    assert response.json()["planned_routes"]

