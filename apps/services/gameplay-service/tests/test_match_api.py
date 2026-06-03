from datetime import UTC, datetime
from uuid import UUID

import pytest
from app.domain.entities import create_match
from app.main import app
from httpx import ASGITransport, AsyncClient


@pytest.mark.anyio
async def test_get_match_returns_st302_state() -> None:
    app.state.match_repository.clear()
    match = create_match(
        player_id=UUID("11111111-1111-4111-8111-111111111302"),
        opponent_id=UUID("22222222-2222-4222-8222-222222222302"),
        player_deck_card_ids=deck_ids("aaaaaaaa-aaaa-4aaa-8aaa", 1),
        opponent_deck_card_ids=deck_ids("bbbbbbbb-bbbb-4bbb-8bbb", 1),
        match_id=UUID("33333333-3333-4333-8333-333333333302"),
        created_at=datetime(2026, 6, 29, tzinfo=UTC),
    )
    app.state.match_repository.save(match)

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        response = await client.get(f"/match/{match.id}")

    payload = response.json()

    assert response.status_code == 200
    assert payload["id"] == str(match.id)
    assert payload["player"]["id"] == str(match.player.id)
    assert payload["opponent"]["id"] == str(match.opponent.id)
    assert payload["status"] == "in_progress"
    assert payload["rounds"] == []
    assert payload["score"] == {"player": 0, "opponent": 0}
    assert payload["winner_id"] is None


@pytest.mark.anyio
async def test_get_unknown_match_returns_not_found() -> None:
    app.state.match_repository.clear()
    match_id = UUID("33333333-3333-4333-8333-333333333302")

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        response = await client.get(f"/match/{match_id}")

    assert response.status_code == 404
    assert response.json()["detail"] == "Match not found."


def deck_ids(prefix: str, start: int) -> tuple[UUID, ...]:
    return tuple(UUID(f"{prefix}-{index:012d}") for index in range(start, start + 10))
