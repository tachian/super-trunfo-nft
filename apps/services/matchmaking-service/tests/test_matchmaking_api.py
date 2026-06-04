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
    assert openapi["paths"]["/matchmaking/find"]["post"]["operationId"] == "findMatch"
    assert "MatchmakingQueuesResponse" in openapi["components"]["schemas"]
    assert "FindMatchRequest" in openapi["components"]["schemas"]
    assert "FindMatchResponse" in openapi["components"]["schemas"]


@pytest.mark.anyio
async def test_find_match_queues_player_when_no_opponent_is_available() -> None:
    app.state.matchmaking_queue_repository.clear()

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        response = await client.post(
            "/matchmaking/find",
            json={
                "player_id": "11111111-1111-4111-8111-000000000402",
                "average_deck_level": 320,
            },
        )

    payload = response.json()

    assert response.status_code == 202
    assert payload["status"] == "queued"
    assert payload["tolerance"] == 20
    assert payload["ticket"]["tier"] == "bronze"
    assert payload["ticket"]["queue"] == "queue:bronze"
    assert payload["matched_ticket"] is None


@pytest.mark.anyio
async def test_find_match_pairs_players_within_level_tolerance() -> None:
    app.state.matchmaking_queue_repository.clear()

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        first_response = await client.post(
            "/matchmaking/find",
            json={
                "player_id": "11111111-1111-4111-8111-000000000402",
                "average_deck_level": 320,
            },
        )
        second_response = await client.post(
            "/matchmaking/find",
            json={
                "player_id": "22222222-2222-4222-8222-000000000402",
                "average_deck_level": 340,
            },
        )

    first_payload = first_response.json()
    second_payload = second_response.json()

    assert first_payload["status"] == "queued"
    assert second_response.status_code == 202
    assert second_payload["status"] == "matched"
    assert second_payload["matched_ticket"]["id"] == first_payload["ticket"]["id"]
