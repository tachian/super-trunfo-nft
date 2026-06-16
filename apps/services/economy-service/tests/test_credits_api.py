from uuid import UUID

import pytest
from app.main import app
from httpx import ASGITransport, AsyncClient

PLAYER_ID = UUID("11111111-1111-4111-8111-000000000501")
MATCH_ID = UUID("22222222-2222-4222-8222-000000000501")


@pytest.mark.anyio
async def test_apply_match_victory_returns_wallet_credit_and_event() -> None:
    app.state.wallet_repository.clear()
    app.state.domain_event_publisher.clear()

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        response = await client.post(
            "/wallet/credits/match-result",
            json={
                "player_id": str(PLAYER_ID),
                "match_id": str(MATCH_ID),
                "result": "victory",
            },
        )

    payload = response.json()

    assert response.status_code == 201
    assert payload["task"] == "ST-501"
    assert payload["created"] is True
    assert payload["awarded_credits"] == 1
    assert payload["balance"] == 1
    assert payload["ledger_entry"]["reason"] == "match_victory"
    assert payload["events"][0]["name"] == "CreditsEarned"


@pytest.mark.anyio
async def test_apply_match_defeat_returns_zero_credit_without_event() -> None:
    app.state.wallet_repository.clear()
    app.state.domain_event_publisher.clear()

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        response = await client.post(
            "/wallet/credits/match-result",
            json={
                "player_id": str(PLAYER_ID),
                "match_id": str(MATCH_ID),
                "result": "defeat",
            },
        )

    payload = response.json()

    assert response.status_code == 201
    assert payload["created"] is True
    assert payload["awarded_credits"] == 0
    assert payload["balance"] == 0
    assert payload["ledger_entry"]["reason"] == "match_defeat"
    assert payload["events"] == []


@pytest.mark.anyio
async def test_get_wallet_credits_returns_balance() -> None:
    app.state.wallet_repository.clear()
    app.state.domain_event_publisher.clear()

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        await client.post(
            "/wallet/credits/match-result",
            json={
                "player_id": str(PLAYER_ID),
                "match_id": str(MATCH_ID),
                "result": "victory",
            },
        )
        response = await client.get(
            "/wallet/credits",
            params={"player_id": str(PLAYER_ID)},
        )

    payload = response.json()

    assert response.status_code == 200
    assert payload["player_id"] == str(PLAYER_ID)
    assert payload["balance"] == 1
    assert payload["ledger_entries"][0]["amount"] == 1


@pytest.mark.anyio
async def test_get_wallet_credits_returns_not_found() -> None:
    app.state.wallet_repository.clear()

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        response = await client.get(
            "/wallet/credits",
            params={"player_id": str(PLAYER_ID)},
        )

    assert response.status_code == 404
    assert response.json()["detail"] == "Wallet not found."


def test_economy_openapi_exposes_st501_operations() -> None:
    openapi = app.openapi()

    assert (
        openapi["paths"]["/wallet/credits/match-result"]["post"]["operationId"]
        == "applyMatchResultCredits"
    )
    assert openapi["paths"]["/wallet/credits"]["get"]["operationId"] == "getWalletCredits"
    assert "ApplyMatchResultCreditsRequest" in openapi["components"]["schemas"]
    assert "ApplyMatchResultCreditsResponse" in openapi["components"]["schemas"]
