from datetime import UTC, datetime
from uuid import UUID

import pytest
from app.domain.entities import Rating
from app.main import app
from httpx import ASGITransport, AsyncClient

WINNER_ID = UUID("11111111-1111-4111-8111-000000000503")
LOSER_ID = UUID("22222222-2222-4222-8222-000000000503")
MATCH_ID = UUID("33333333-3333-4333-8333-000000000503")
FRIEND_ID = UUID("44444444-4444-4444-8444-000000000503")


@pytest.fixture(autouse=True)
def reset_ranking_state() -> None:
    app.state.rating_repository.clear()
    app.state.leaderboard_cache.clear()
    app.state.domain_event_publisher.clear()


@pytest.mark.anyio
async def test_recalculate_ranking_updates_winner_and_loser_ratings() -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        response = await client.post(
            "/ranking/recalculate",
            json={
                "match_id": str(MATCH_ID),
                "winner_id": str(WINNER_ID),
                "loser_id": str(LOSER_ID),
            },
        )

    payload = response.json()

    assert response.status_code == 201
    assert payload["task"] == "ST-503"
    assert payload["created"] is True
    assert payload["winner"]["score"] == 1016
    assert payload["winner"]["tier"] == "silver"
    assert payload["loser"]["score"] == 984
    assert payload["loser"]["tier"] == "bronze"
    assert [event["name"] for event in payload["events"]] == [
        "PlayerRankUpdated",
        "PlayerRankUpdated",
    ]


@pytest.mark.anyio
async def test_recalculate_ranking_is_idempotent_per_match() -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        await client.post(
            "/ranking/recalculate",
            json={
                "match_id": str(MATCH_ID),
                "winner_id": str(WINNER_ID),
                "loser_id": str(LOSER_ID),
            },
        )
        response = await client.post(
            "/ranking/recalculate",
            json={
                "match_id": str(MATCH_ID),
                "winner_id": str(WINNER_ID),
                "loser_id": str(LOSER_ID),
            },
        )

    payload = response.json()

    assert response.status_code == 201
    assert payload["created"] is False
    assert payload["winner"]["score"] == 1016
    assert payload["loser"]["score"] == 984
    assert payload["events"] == []


@pytest.mark.anyio
async def test_recalculate_ranking_rejects_same_winner_and_loser() -> None:
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        response = await client.post(
            "/ranking/recalculate",
            json={
                "match_id": str(MATCH_ID),
                "winner_id": str(WINNER_ID),
                "loser_id": str(WINNER_ID),
            },
        )

    assert response.status_code == 400
    assert response.json()["detail"] == "winner and loser must be different players"


def test_ranking_openapi_exposes_st503_operations() -> None:
    openapi = app.openapi()

    assert (
        openapi["paths"]["/ranking/recalculate"]["post"]["operationId"]
        == "recalculatePlayerRating"
    )
    assert "RecalculatePlayerRatingRequest" in openapi["components"]["schemas"]
    assert "RecalculatePlayerRatingResponse" in openapi["components"]["schemas"]


@pytest.mark.anyio
async def test_global_ranking_returns_cached_leaderboard() -> None:
    app.state.rating_repository.save_many(
        (
            rating(WINNER_ID, score=1300, wins=3),
            rating(LOSER_ID, score=1100, wins=1),
            rating(FRIEND_ID, score=1200, wins=2),
        )
    )

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        first_response = await client.get(
            "/ranking/global",
            params={"limit": 2, "offset": 0},
        )
        cached_response = await client.get(
            "/ranking/global",
            params={"limit": 2, "offset": 0},
        )

    first_payload = first_response.json()
    cached_payload = cached_response.json()

    assert first_response.status_code == 200
    assert first_payload["task"] == "ST-504"
    assert first_payload["scope"] == "global"
    assert first_payload["total"] == 3
    assert first_payload["cache"]["hit"] is False
    assert [entry["position"] for entry in first_payload["entries"]] == [1, 2]
    assert [entry["player_id"] for entry in first_payload["entries"]] == [
        str(WINNER_ID),
        str(FRIEND_ID),
    ]
    assert cached_response.status_code == 200
    assert cached_payload["cache"]["hit"] is True
    assert cached_payload["entries"] == first_payload["entries"]


@pytest.mark.anyio
async def test_friends_ranking_returns_empty_without_friends() -> None:
    app.state.rating_repository.save_many((rating(FRIEND_ID, score=1300),))

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        response = await client.get(
            "/ranking/friends",
            params={"player_id": str(WINNER_ID)},
        )

    payload = response.json()

    assert response.status_code == 200
    assert payload["task"] == "ST-504"
    assert payload["scope"] == "friends"
    assert payload["entries"] == []
    assert payload["total"] == 0


@pytest.mark.anyio
async def test_friends_ranking_filters_supplied_friend_ids() -> None:
    app.state.rating_repository.save_many(
        (
            rating(WINNER_ID, score=1400),
            rating(FRIEND_ID, score=1300),
            rating(LOSER_ID, score=900),
        )
    )

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        response = await client.get(
            "/ranking/friends",
            params={
                "player_id": str(WINNER_ID),
                "friend_ids": str(FRIEND_ID),
            },
        )

    payload = response.json()

    assert response.status_code == 200
    assert payload["total"] == 1
    assert payload["entries"][0]["player_id"] == str(FRIEND_ID)


def test_ranking_openapi_exposes_st504_operations() -> None:
    openapi = app.openapi()

    assert openapi["paths"]["/ranking/global"]["get"]["operationId"] == "getGlobalRanking"
    assert openapi["paths"]["/ranking/friends"]["get"]["operationId"] == "getFriendsRanking"
    assert "RankingLeaderboardResponse" in openapi["components"]["schemas"]
    assert "LeaderboardEntryResponse" in openapi["components"]["schemas"]


def rating(player_id: UUID, *, score: int, wins: int = 0) -> Rating:
    return Rating(
        player_id=player_id,
        score=score,
        wins=wins,
        updated_at=datetime(2026, 6, 16, tzinfo=UTC),
    )
