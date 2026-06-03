from uuid import UUID

import pytest
from app.main import app
from httpx import ASGITransport, AsyncClient


@pytest.mark.anyio
async def test_generate_and_get_offline_metadata() -> None:
    app.state.nft_metadata_repository.clear()
    app.state.domain_event_publisher.clear()
    card_id = "22222222-2222-4222-8222-222222222205"

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        create_response = await client.post(
            "/nft/metadata/offline",
            json={
                "card_id": card_id,
                "name": "Solar Titan",
                "family": "solar",
                "rarity": 80,
                "level": 334,
                "speed": 70,
                "strength": 62,
                "intelligence": 58,
                "resistance": 64,
            },
        )
        get_response = await client.get(f"/nft/metadata/{card_id}")

    created_metadata = create_response.json()
    saved_metadata = get_response.json()

    assert create_response.status_code == 201
    assert get_response.status_code == 200
    assert created_metadata == saved_metadata
    assert saved_metadata["name"] == "Super Trunfo NFT - Solar Titan"
    assert saved_metadata["image"].startswith("ipfs://super-trunfo-nft/cards/")
    assert saved_metadata["properties"]["card_id"] == card_id
    assert saved_metadata["properties"]["mint_enabled"] is False
    assert app.state.domain_event_publisher.published_events()[0].name == "NftMetadataGenerated"


@pytest.mark.anyio
async def test_get_unknown_metadata_returns_not_found() -> None:
    app.state.nft_metadata_repository.clear()
    card_id = UUID("33333333-3333-4333-8333-333333333205")

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        response = await client.get(f"/nft/metadata/{card_id}")

    assert response.status_code == 404
    assert response.json()["detail"] == "Offline NFT metadata not found."


@pytest.mark.anyio
async def test_mint_endpoint_remains_disabled_for_mvp() -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        response = await client.post("/nft/mint")

    payload = response.json()

    assert response.status_code == 202
    assert payload["status"] == "disabled"
    assert payload["task"] == "ST-701"
