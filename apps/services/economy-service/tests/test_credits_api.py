from datetime import UTC, datetime, timedelta
from uuid import UUID

import pytest
from app.domain.entities import MatchResult, ShopOffer, create_wallet
from app.infrastructure.repositories import InMemoryShopOfferRepository
from app.main import app
from httpx import ASGITransport, AsyncClient

PLAYER_ID = UUID("11111111-1111-4111-8111-000000000501")
MATCH_ID = UUID("22222222-2222-4222-8222-000000000501")
SHOP_OFFER_ID = UUID("11111111-5020-4502-8502-000000000001")
EXPENSIVE_SHOP_OFFER_ID = UUID("11111111-5020-4502-8502-000000000002")
SECOND_PLAYER_ID = UUID("33333333-3333-4333-8333-000000000505")


@pytest.fixture(autouse=True)
def reset_economy_state() -> None:
    app.state.wallet_repository.clear()
    app.state.domain_event_publisher.clear()
    app.state.shop_offer_repository = InMemoryShopOfferRepository.with_default_offers()


@pytest.mark.anyio
async def test_apply_match_victory_returns_wallet_credit_and_event() -> None:
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


@pytest.mark.anyio
async def test_list_shop_offers_returns_active_prices_and_expiration() -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        response = await client.get("/shop/offers")

    payload = response.json()

    assert response.status_code == 200
    assert payload["task"] == "ST-502"
    assert [offer["price"] for offer in payload["offers"]] == [1, 2]
    assert payload["offers"][0]["id"] == str(SHOP_OFFER_ID)
    assert payload["offers"][0]["expires_at"]


@pytest.mark.anyio
async def test_buy_shop_offer_debits_wallet_and_adds_inventory_card() -> None:
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
        response = await client.post(
            "/shop/buy",
            json={
                "player_id": str(PLAYER_ID),
                "offer_id": str(SHOP_OFFER_ID),
            },
        )
        wallet_response = await client.get(
            "/wallet/credits",
            params={"player_id": str(PLAYER_ID)},
        )

    payload = response.json()

    assert response.status_code == 201
    assert payload["task"] == "ST-502"
    assert payload["balance"] == 0
    assert payload["offer"]["price"] == 1
    assert payload["purchase"]["offer_id"] == str(SHOP_OFFER_ID)
    assert payload["inventory_card"]["card_id"] == payload["offer"]["card_id"]
    assert payload["events"][0]["name"] == "OfferPurchased"
    assert wallet_response.json()["balance"] == 0


@pytest.mark.anyio
async def test_buy_shop_offer_rejects_insufficient_credits() -> None:
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
        response = await client.post(
            "/shop/buy",
            json={
                "player_id": str(PLAYER_ID),
                "offer_id": str(EXPENSIVE_SHOP_OFFER_ID),
            },
        )

    assert response.status_code == 409
    assert response.json()["detail"] == "Insufficient credits."


@pytest.mark.anyio
async def test_buy_shop_offer_rejects_expired_offer() -> None:
    expired_offer = ShopOffer(
        id=UUID("11111111-5020-4502-8502-000000000099"),
        card_id=UUID("22222222-5020-4502-8502-000000000099"),
        card_name="Carta Expirada",
        family="legacy",
        rarity=42,
        price=1,
        expires_at=datetime.now(UTC) - timedelta(days=1),
    )
    app.state.shop_offer_repository.clear()
    app.state.shop_offer_repository.save(expired_offer)

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
        response = await client.post(
            "/shop/buy",
            json={
                "player_id": str(PLAYER_ID),
                "offer_id": str(expired_offer.id),
            },
        )

    assert response.status_code == 409
    assert response.json()["detail"] == "Shop offer expired."


def test_economy_openapi_exposes_st501_operations() -> None:
    openapi = app.openapi()

    assert (
        openapi["paths"]["/wallet/credits/match-result"]["post"]["operationId"]
        == "applyMatchResultCredits"
    )
    assert openapi["paths"]["/wallet/credits"]["get"]["operationId"] == "getWalletCredits"
    assert "ApplyMatchResultCreditsRequest" in openapi["components"]["schemas"]
    assert "ApplyMatchResultCreditsResponse" in openapi["components"]["schemas"]


def test_economy_openapi_exposes_st502_operations() -> None:
    openapi = app.openapi()

    assert openapi["paths"]["/shop/offers"]["get"]["operationId"] == "listShopOffers"
    assert openapi["paths"]["/shop/buy"]["post"]["operationId"] == "buyShopOffer"
    assert "BuyShopOfferRequest" in openapi["components"]["schemas"]
    assert "BuyShopOfferResponse" in openapi["components"]["schemas"]
    assert "ShopOfferResponse" in openapi["components"]["schemas"]


@pytest.mark.anyio
async def test_get_economic_telemetry_returns_aggregate_metrics() -> None:
    wallet = create_wallet(PLAYER_ID)
    second_wallet = create_wallet(SECOND_PLAYER_ID)

    for index in range(1, 6):
        wallet, _, _ = wallet.apply_match_result(
            match_id=UUID(f"44444444-4444-4444-8444-{index:012d}"),
            result=MatchResult.VICTORY,
        )

    second_wallet, _, _ = second_wallet.apply_match_result(
        match_id=UUID("55555555-5555-4555-8555-000000000001"),
        result=MatchResult.VICTORY,
    )
    second_wallet, _, _ = second_wallet.buy_offer(
        offer=app.state.shop_offer_repository.find_by_id(SHOP_OFFER_ID)
    )
    app.state.wallet_repository.save(wallet)
    app.state.wallet_repository.save(second_wallet)

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        response = await client.get("/economy/telemetry")

    payload = response.json()

    assert response.status_code == 200
    assert payload["task"] == "ST-505"
    assert payload["balances"]["wallet_count"] == 2
    assert payload["credits"]["total_credits_earned"] == 6
    assert payload["credits"]["total_credits_spent"] == 1
    assert payload["credits"]["total_purchases"] == 1
    assert payload["risk"]["highest_win_streak"] == 5
    assert payload["risk"]["abuse_signal_count"] == 1
    assert payload["risk"]["inflation_status"] == "critical"
    assert "player_id" not in payload


def test_economy_openapi_exposes_st505_operations() -> None:
    openapi = app.openapi()

    assert (
        openapi["paths"]["/economy/telemetry"]["get"]["operationId"]
        == "getEconomicTelemetry"
    )
    assert "EconomicTelemetryResponse" in openapi["components"]["schemas"]
    assert "EconomicRiskTelemetryResponse" in openapi["components"]["schemas"]
