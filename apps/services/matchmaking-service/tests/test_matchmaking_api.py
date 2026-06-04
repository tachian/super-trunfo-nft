import pytest
from app.main import app
from httpx import ASGITransport, AsyncClient


@pytest.mark.anyio
async def test_matchmaking_queues_returns_st401_redis_tier_queues() -> None:
    app.state.matchmaking_queue_repository.clear()

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        response = await client.get("/matchmaking/queues")

    payload = response.json()

    assert response.status_code == 200
    assert payload["service"] == "matchmaking-service"
    assert payload["task"] == "ST-401"
    assert payload["backend"] == "redis"
    assert payload["queues"] == [
        {"tier": "bronze", "name": "queue:bronze", "size": 0},
        {"tier": "silver", "name": "queue:silver", "size": 0},
        {"tier": "gold", "name": "queue:gold", "size": 0},
    ]


def test_matchmaking_openapi_exposes_queue_operation() -> None:
    openapi = app.openapi()

    assert (
        openapi["paths"]["/matchmaking/queues"]["get"]["operationId"]
        == "getMatchmakingQueues"
    )
    assert "MatchmakingQueuesResponse" in openapi["components"]["schemas"]
