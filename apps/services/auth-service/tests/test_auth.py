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
    assert body["player"]["credits"] == 1
    assert "email" not in body["player"]
    assert body["access_token"].count(".") == 2
    assert jwt_payload(body["access_token"])["sub"] == body["player"]["id"]
    assert_initial_onboarding(body["onboarding"])


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
    assert_initial_onboarding(body["onboarding"])


@pytest.mark.anyio
async def test_current_player_profile_returns_authenticated_profile() -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        register_response = await client.post(
            "/auth/register",
            json={
                "nickname": "ProfilePlayer",
                "email": "profile@example.com",
                "password": "strong-password",
            },
        )
        access_token = register_response.json()["access_token"]
        profile_response = await client.get(
            "/players/me",
            headers={"Authorization": f"Bearer {access_token}"},
        )

    body = profile_response.json()

    assert profile_response.status_code == 200
    assert body["id"] == register_response.json()["player"]["id"]
    assert body["nickname"] == "ProfilePlayer"
    assert body["rating"] == 1000
    assert body["credits"] == 1
    assert body["created_at"]
    assert body["social_login"] == {"provider": "credentials", "subject": None}
    assert_initial_onboarding(body["onboarding"])
    assert "email" not in body


@pytest.mark.anyio
async def test_current_player_profile_keeps_initial_onboarding_idempotent() -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        register_response = await client.post(
            "/auth/register",
            json={
                "nickname": "IdempotentPlayer",
                "email": "idempotent@example.com",
                "password": "strong-password",
            },
        )
        access_token = register_response.json()["access_token"]
        first_profile_response = await client.get(
            "/players/me",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        second_profile_response = await client.get(
            "/players/me",
            headers={"Authorization": f"Bearer {access_token}"},
        )

    first_profile = first_profile_response.json()
    second_profile = second_profile_response.json()

    assert first_profile["credits"] == 1
    assert second_profile["credits"] == 1
    assert first_profile["onboarding"] == second_profile["onboarding"]


@pytest.mark.anyio
async def test_current_player_profile_requires_bearer_token() -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        response = await client.get("/players/me")

    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid or missing bearer token."}


@pytest.mark.anyio
async def test_current_player_profile_rejects_invalid_bearer_token() -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        response = await client.get(
            "/players/me",
            headers={"Authorization": "Bearer invalid-token"},
        )

    assert response.status_code == 401
    assert response.json() == {"detail": "Invalid or missing bearer token."}


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


def assert_initial_onboarding(onboarding: dict[str, object]) -> None:
    initial_deck = onboarding["initial_deck"]
    credit_ledger = onboarding["credit_ledger"]
    levels = [card["level"] for card in initial_deck]

    assert onboarding["initial_credits"] == 1
    assert len(initial_deck) == 9
    assert len({card["id"] for card in initial_deck}) == 9
    assert all(card["rarity_label"] != "legendary" for card in initial_deck)
    assert all(45 <= card["speed"] <= 72 for card in initial_deck)
    assert all(45 <= card["strength"] <= 72 for card in initial_deck)
    assert all(45 <= card["intelligence"] <= 72 for card in initial_deck)
    assert all(45 <= card["resistance"] <= 72 for card in initial_deck)
    assert max(levels) - min(levels) <= 35
    assert credit_ledger == [
        {
            "id": credit_ledger[0]["id"],
            "amount": 1,
            "reason": "initial_deck_tenth_card_credit",
            "created_at": credit_ledger[0]["created_at"],
        }
    ]
