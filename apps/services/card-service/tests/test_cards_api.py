import pytest
from app.main import app
from httpx import ASGITransport, AsyncClient


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
    assert response["expires_at"]
