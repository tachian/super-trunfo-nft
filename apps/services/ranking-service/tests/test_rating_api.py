from uuid import UUID

import pytest
from app.main import app
from httpx import ASGITransport, AsyncClient

WINNER_ID = UUID("11111111-1111-4111-8111-000000000503")
LOSER_ID = UUID("22222222-2222-4222-8222-000000000503")
MATCH_ID = UUID("33333333-3333-4333-8333-000000000503")


@pytest.fixture(autouse=True)
def reset_ranking_state() -> None:
    app.state.rating_repository.clear()
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
