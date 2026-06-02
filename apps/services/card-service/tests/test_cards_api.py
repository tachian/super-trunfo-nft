import pytest
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
