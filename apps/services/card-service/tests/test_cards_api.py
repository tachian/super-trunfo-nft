from uuid import UUID

import pytest
from app.domain.entities import create_card
from app.main import app
from httpx import ASGITransport, AsyncClient
from super_trunfo_shared.cards import CardAttributes


@pytest.mark.anyio
async def test_sample_card_model_exposes_st201_aggregate_shape() -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        api_response = await client.get("/cards/sample/model")

    response = api_response.json()

    assert api_response.status_code == 200
    assert response["id"] == "22222222-2222-4222-8222-222222222222"
    assert response["owner_id"] == "11111111-1111-4111-8111-111111111111"
    assert response["name"] == "Shadow Titan"
    assert response["family"] == "shadow"
    assert response["speed"] == 82
    assert response["strength"] == 91
    assert response["intelligence"] == 64
    assert response["resistance"] == 76
    assert response["rarity"] == 80
    assert response["level"] == 393
    assert len(response["uniqueness_hash"]) == 64
    assert response["expiration_days"] == 401
    assert response["expires_at"]


@pytest.mark.anyio
async def test_generate_sample_card_persists_unique_card_hash() -> None:
    original_repository = app.state.card_repository
    original_generator = app.state.card_attribute_generator
    app.state.card_repository.clear()
    app.state.card_attribute_generator = StaticAttributeGenerator()

    try:
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
        ) as client:
            api_response = await client.post(
                "/cards/sample/generate",
                json={
                    "owner_id": "11111111-1111-4111-8111-111111111111",
                    "family": "shadow",
                },
            )
    finally:
        app.state.card_repository.clear()
        app.state.card_repository = original_repository
        app.state.card_attribute_generator = original_generator

    response = api_response.json()

    assert api_response.status_code == 201
    assert response["attempts"] == 1
    assert response["card"]["name"] == "Shadow Titan"
    assert response["card"]["family"] == "shadow"
    assert len(response["card"]["uniqueness_hash"]) == 64
    assert response["card"]["expiration_days"] == 401


@pytest.mark.anyio
async def test_select_deck_returns_active_deck_for_10_owned_valid_cards() -> None:
    app.state.card_repository.clear()
    app.state.deck_repository.clear()
    app.state.domain_event_publisher.clear()
    owner_id = "11111111-1111-4111-8111-111111111301"
    cards = [
        create_card(
            owner_id=UUID(owner_id),
            attributes=CardAttributes(
                name=f"Deck API Card {index}",
                speed=50 + index,
                strength=60,
                intelligence=70,
                resistance=80,
                rarity=50,
            ),
            family="solar",
            card_id=UUID(f"44444444-4444-4444-8444-{index:012d}"),
        )
        for index in range(1, 11)
    ]

    for card in cards:
        app.state.card_repository.add(card)

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        api_response = await client.post(
            "/cards/select-deck",
            json={
                "owner_id": owner_id,
                "card_ids": [str(card.id) for card in cards],
            },
        )

    response = api_response.json()

    assert api_response.status_code == 200
    assert response["owner_id"] == owner_id
    assert response["card_ids"] == [str(card.id) for card in cards]
    assert response["average_level"] == 315.5
    assert response["selected_at"]
    assert app.state.domain_event_publisher.published_events()[0].name == "DeckSelected"


@pytest.mark.anyio
async def test_select_deck_rejects_duplicate_card_ids() -> None:
    owner_id = "11111111-1111-4111-8111-111111111301"
    card_id = "44444444-4444-4444-8444-000000000001"

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        api_response = await client.post(
            "/cards/select-deck",
            json={
                "owner_id": owner_id,
                "card_ids": [card_id] * 10,
            },
        )

    assert api_response.status_code == 400
    assert "duplicated" in api_response.json()["detail"]


class StaticAttributeGenerator:
    def generate(self) -> CardAttributes:
        return CardAttributes(
            name="Shadow Titan",
            speed=82,
            strength=91,
            intelligence=64,
            resistance=76,
            rarity=80,
        )
