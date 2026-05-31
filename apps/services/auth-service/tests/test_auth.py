import base64
import json
import logging

import pytest
from app.main import app
from httpx import ASGITransport, AsyncClient


@pytest.fixture(autouse=True)
def clear_player_repository() -> None:
    app.state.player_repository.clear()


@pytest.mark.anyio
async def test_register_player_returns_jwt_without_sensitive_player_data() -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        response = await client.post(
            "/auth/register",
            json={
                "nickname": "Tachian",
                "email": "tachian@example.com",
                "password": "strong-password",
            },
        )

    body = response.json()

    assert response.status_code == 201
    assert body["token_type"] == "bearer"
    assert body["expires_in"] == 3600
    assert body["player"]["nickname"] == "Tachian"
    assert "email" not in body["player"]
    assert body["access_token"].count(".") == 2
    assert jwt_payload(body["access_token"])["sub"] == body["player"]["id"]


@pytest.mark.anyio
async def test_login_player_returns_jwt_for_existing_player() -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        await client.post(
            "/auth/register",
            json={
                "nickname": "PlayerOne",
                "email": "player@example.com",
                "password": "strong-password",
            },
        )
        response = await client.post(
            "/auth/login",
            json={"email": "player@example.com", "password": "strong-password"},
        )

    body = response.json()

    assert response.status_code == 200
    assert body["token_type"] == "bearer"
    assert body["player"]["nickname"] == "PlayerOne"


@pytest.mark.anyio
async def test_duplicate_player_is_rejected() -> None:
    payload = {
        "nickname": "Duplicate",
        "email": "duplicate@example.com",
        "password": "strong-password",
    }

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        first_response = await client.post("/auth/register", json=payload)
        second_response = await client.post("/auth/register", json=payload)

    assert first_response.status_code == 201
    assert second_response.status_code == 409


@pytest.mark.anyio
async def test_invalid_login_uses_safe_error_message() -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        response = await client.post(
            "/auth/login",
            json={"email": "unknown@example.com", "password": "strong-password"},
        )

    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid credentials."}


@pytest.mark.anyio
async def test_auth_request_logs_mask_sensitive_payload(caplog: pytest.LogCaptureFixture) -> None:
    caplog.set_level(logging.INFO)

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        await client.post(
            "/auth/register",
            json={
                "nickname": "Log Player",
                "email": "logs@example.com",
                "password": "strong-password",
            },
        )

    request_logs = [
        record
        for record in caplog.records
        if getattr(record, "event", None) == "http.request.received"
        and getattr(record, "path", None) == "/auth/register"
    ]

    assert request_logs
    assert request_logs[-1].request_body["email"] == "l***@example.com"
    assert request_logs[-1].request_body["password"] == "[REDACTED]"
    assert request_logs[-1].request_body["nickname"] == "Log Player"


def jwt_payload(token: str) -> dict[str, object]:
    encoded_payload = token.split(".")[1]
    padded_payload = f"{encoded_payload}{'=' * (-len(encoded_payload) % 4)}"
    return json.loads(base64.urlsafe_b64decode(padded_payload).decode("utf-8"))
