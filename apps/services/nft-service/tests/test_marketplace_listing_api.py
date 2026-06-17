from datetime import UTC, datetime, timedelta

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


SELLER_ID = "11111111-7030-4703-8703-000000000001"
CARD_ID = "22222222-7030-4703-8703-000000000001"


@pytest.mark.anyio
async def test_create_and_list_marketplace_listing() -> None:
    app.state.marketplace_listing_repository.clear()
    app.state.domain_event_publisher.clear()
    expires_at = datetime.now(UTC) + timedelta(days=7)

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        create_response = await client.post(
            "/marketplace/listings",
            json={
                "seller_id": SELLER_ID,
                "card_id": CARD_ID,
                "token_id": 703,
                "price": 5,
                "expires_at": expires_at.isoformat(),
            },
        )
        list_response = await client.get("/marketplace/listings")

    created_listing = create_response.json()
    listed_listings = list_response.json()

    assert create_response.status_code == 201
    assert list_response.status_code == 200
    assert created_listing["seller_id"] == SELLER_ID
    assert created_listing["card_id"] == CARD_ID
    assert created_listing["token_id"] == 703
    assert created_listing["price"] == 5
    assert created_listing["status"] == "active"
    assert created_listing["history"][0]["reason"] == "listing created"
    assert listed_listings == [created_listing]
    assert app.state.domain_event_publisher.published_events()[0].name == (
        "MarketplaceListingCreated"
    )


@pytest.mark.anyio
async def test_create_marketplace_listing_rejects_expired_payload() -> None:
    app.state.marketplace_listing_repository.clear()
    created_before_now = datetime.now(UTC) - timedelta(days=1)

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        response = await client.post(
            "/marketplace/listings",
            json={
                "seller_id": SELLER_ID,
                "card_id": CARD_ID,
                "token_id": 703,
                "price": 5,
                "expires_at": created_before_now.isoformat(),
            },
        )

    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid marketplace listing."


@pytest.mark.anyio
async def test_marketplace_routes_are_registered() -> None:
    route_paths = {getattr(route, "path", None) for route in app.routes}

    assert "/marketplace/listings" in route_paths
