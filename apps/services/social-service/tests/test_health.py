import pytest
from app.main import SERVICE_NAME, app
from super_trunfo_shared.testing import call_registered_route


@pytest.mark.anyio
async def test_healthcheck_returns_service_name() -> None:
    response = await call_registered_route(app, "/health")

    assert response["service"] == SERVICE_NAME


@pytest.mark.anyio
async def test_context_lists_planned_routes() -> None:
    response = await call_registered_route(app, "/context")

    assert response["planned_routes"]
