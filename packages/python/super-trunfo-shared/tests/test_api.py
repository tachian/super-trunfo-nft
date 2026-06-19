import pytest
from httpx import ASGITransport, AsyncClient
from super_trunfo_shared.api import cors_origins_from_environment, create_service_app


def test_cors_origins_are_empty_by_default(monkeypatch) -> None:
    monkeypatch.delenv("SUPER_TRUNFO_CORS_ORIGINS", raising=False)

    assert cors_origins_from_environment() == []


def test_cors_origins_can_be_configured_for_local_development(monkeypatch) -> None:
    monkeypatch.setenv(
        "SUPER_TRUNFO_CORS_ORIGINS",
        "http://localhost:3000, http://127.0.0.1:3000",
    )

    assert cors_origins_from_environment() == [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]


@pytest.mark.anyio
async def test_service_app_adds_owasp_security_headers(monkeypatch) -> None:
    monkeypatch.setenv("SUPER_TRUNFO_RATE_LIMIT_ENABLED", "false")
    app = create_test_app()

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        response = await client.get("/health")

    assert response.status_code == 200
    assert response.headers["x-content-type-options"] == "nosniff"
    assert response.headers["x-frame-options"] == "DENY"
    assert response.headers["referrer-policy"] == "no-referrer"
    assert response.headers["permissions-policy"] == "geolocation=(), microphone=(), camera=()"
    assert response.headers["cache-control"] == "no-store"


@pytest.mark.anyio
async def test_service_app_rate_limits_non_platform_routes(monkeypatch) -> None:
    monkeypatch.setenv("SUPER_TRUNFO_RATE_LIMIT_ENABLED", "true")
    monkeypatch.setenv("SUPER_TRUNFO_RATE_LIMIT_REQUESTS", "2")
    monkeypatch.setenv("SUPER_TRUNFO_RATE_LIMIT_WINDOW_SECONDS", "60")
    monkeypatch.setenv("SUPER_TRUNFO_RATE_LIMIT_EXCLUDED_PATHS", "/health,/ready,/context")
    app = create_test_app()

    @app.get("/limited")
    async def limited() -> dict[str, str]:
        return {"status": "ok"}

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        first_response = await client.get("/limited")
        second_response = await client.get("/limited")
        third_response = await client.get("/limited")
        health_response = await client.get("/health")

    assert first_response.status_code == 200
    assert second_response.status_code == 200
    assert third_response.status_code == 429
    assert third_response.json()["detail"] == "Too many requests."
    assert third_response.headers["x-ratelimit-limit"] == "2"
    assert health_response.status_code == 200


@pytest.mark.anyio
async def test_service_app_rejects_oversized_body(monkeypatch) -> None:
    monkeypatch.setenv("SUPER_TRUNFO_RATE_LIMIT_ENABLED", "false")
    monkeypatch.setenv("SUPER_TRUNFO_MAX_REQUEST_BODY_BYTES", "8")
    app = create_test_app()

    @app.post("/payload")
    async def payload() -> dict[str, str]:
        return {"status": "accepted"}

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        response = await client.post("/payload", json={"message": "too large"})

    assert response.status_code == 413
    assert response.json()["detail"] == "Request body is too large."


@pytest.mark.anyio
async def test_service_app_rejects_non_json_write_requests(monkeypatch) -> None:
    monkeypatch.setenv("SUPER_TRUNFO_RATE_LIMIT_ENABLED", "false")
    app = create_test_app()

    @app.post("/payload")
    async def payload() -> dict[str, str]:
        return {"status": "accepted"}

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        response = await client.post(
            "/payload",
            content="plain text",
            headers={"content-type": "text/plain"},
        )

    assert response.status_code == 415
    assert response.json()["detail"] == "Unsupported media type."


def create_test_app():
    return create_service_app(
        service_name="test-service",
        context="test",
        planned_routes=(),
    )
