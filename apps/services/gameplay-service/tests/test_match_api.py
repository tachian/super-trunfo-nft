from datetime import UTC, datetime
from types import SimpleNamespace
from uuid import UUID

import pytest
from app.api.routes import create_gameplay_router
from app.domain.entities import create_match
from app.main import app
from fastapi import WebSocketDisconnect
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


@pytest.mark.anyio
async def test_play_round_unknown_match_returns_not_found() -> None:
    app.state.match_repository.clear()
    match_id = UUID("33333333-3333-4333-8333-333333333404")

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        response = await client.post(
            f"/match/{match_id}/play",
            json={
                "player_card_id": "aaaaaaaa-aaaa-4aaa-8aaa-000000000001",
                "opponent_card_id": "bbbbbbbb-bbbb-4bbb-8bbb-000000000001",
                "selected_attribute": "speed",
            },
        )

    assert response.status_code == 404
    assert response.json()["detail"] == "Match not found."


@pytest.mark.anyio
async def test_play_round_accepts_valid_cards_and_attribute() -> None:
    match = persisted_match()

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        response = await client.post(
            f"/match/{match.id}/play",
            json={
                "player_card_id": str(match.player.deck_card_ids[0]),
                "opponent_card_id": str(match.opponent.deck_card_ids[0]),
                "selected_attribute": "speed",
            },
        )

    payload = response.json()

    assert response.status_code == 200
    assert payload["id"] == str(match.id)
    assert payload["rounds"][0]["number"] == 1
    assert payload["rounds"][0]["selected_attribute"] == "speed"
    assert payload["score"] == {"player": 0, "opponent": 0}


@pytest.mark.anyio
async def test_play_round_rejects_invalid_card() -> None:
    match = persisted_match()

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        response = await client.post(
            f"/match/{match.id}/play",
            json={
                "player_card_id": "cccccccc-cccc-4ccc-8ccc-000000000001",
                "opponent_card_id": str(match.opponent.deck_card_ids[0]),
                "selected_attribute": "speed",
            },
        )

    assert response.status_code == 400
    assert "player card" in response.json()["detail"]


@pytest.mark.anyio
async def test_play_round_rejects_card_replay() -> None:
    match = persisted_match()

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        await client.post(
            f"/match/{match.id}/play",
            json={
                "player_card_id": str(match.player.deck_card_ids[0]),
                "opponent_card_id": str(match.opponent.deck_card_ids[0]),
                "selected_attribute": "speed",
            },
        )
        response = await client.post(
            f"/match/{match.id}/play",
            json={
                "player_card_id": str(match.player.deck_card_ids[0]),
                "opponent_card_id": str(match.opponent.deck_card_ids[1]),
                "selected_attribute": "strength",
            },
        )

    assert response.status_code == 400
    assert "already played" in response.json()["detail"]


@pytest.mark.anyio
async def test_play_round_rejects_invalid_attribute() -> None:
    match = persisted_match()

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        response = await client.post(
            f"/match/{match.id}/play",
            json={
                "player_card_id": str(match.player.deck_card_ids[0]),
                "opponent_card_id": str(match.opponent.deck_card_ids[0]),
                "selected_attribute": "luck",
            },
        )

    assert response.status_code == 422


@pytest.mark.anyio
async def test_play_round_rejects_client_score_mutation() -> None:
    match = persisted_match()

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        response = await client.post(
            f"/match/{match.id}/play",
            json={
                "player_card_id": str(match.player.deck_card_ids[0]),
                "opponent_card_id": str(match.opponent.deck_card_ids[0]),
                "selected_attribute": "speed",
                "winner_id": str(match.player.id),
                "score": {"player": 10, "opponent": 0},
            },
        )

    assert response.status_code == 422


@pytest.mark.anyio
async def test_match_replay_returns_authoritative_rounds() -> None:
    match = persisted_match()

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        await client.post(
            f"/match/{match.id}/play",
            json={
                "player_card_id": str(match.player.deck_card_ids[0]),
                "opponent_card_id": str(match.opponent.deck_card_ids[0]),
                "selected_attribute": "speed",
            },
        )
        response = await client.get(f"/match/{match.id}/replay")

    payload = response.json()

    assert response.status_code == 200
    assert payload["match_id"] == str(match.id)
    assert payload["rounds"][0]["number"] == 1
    assert payload["rounds"][0]["selected_attribute"] == "speed"


@pytest.mark.anyio
async def test_match_replay_unknown_match_returns_not_found() -> None:
    app.state.match_repository.clear()
    match_id = UUID("33333333-3333-4333-8333-333333333404")

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        response = await client.get(f"/match/{match_id}/replay")

    assert response.status_code == 404
    assert response.json()["detail"] == "Match not found."


@pytest.mark.anyio
async def test_match_api_flow_get_play_get_and_replay() -> None:
    match = persisted_match()

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        initial_response = await client.get(f"/match/{match.id}")
        play_response = await client.post(
            f"/match/{match.id}/play",
            json={
                "player_card_id": str(match.player.deck_card_ids[0]),
                "opponent_card_id": str(match.opponent.deck_card_ids[0]),
                "selected_attribute": "resistance",
            },
        )
        updated_response = await client.get(f"/match/{match.id}")
        replay_response = await client.get(f"/match/{match.id}/replay")

    assert initial_response.status_code == 200
    assert initial_response.json()["rounds"] == []
    assert play_response.status_code == 200
    assert play_response.json()["rounds"][0]["selected_attribute"] == "resistance"
    assert updated_response.status_code == 200
    assert len(updated_response.json()["rounds"]) == 1
    assert replay_response.status_code == 200
    assert replay_response.json()["rounds"] == updated_response.json()["rounds"]


def test_gameplay_routes_include_realtime_websocket() -> None:
    assert realtime_websocket_endpoint(app.routes) is not None


@pytest.mark.anyio
async def test_match_events_websocket_streams_published_events() -> None:
    match = persisted_match()
    app.state.gameplay_realtime_event_bus.clear()
    await play_first_round(match)
    websocket = FakeWebSocket(app)
    websocket_endpoint = realtime_websocket_endpoint(create_gameplay_router().routes)
    assert websocket_endpoint is not None

    await websocket_endpoint(match.id, websocket)

    assert websocket.accepted is True
    assert [event["name"] for event in websocket.sent_messages] == [
        "AttributeSelected",
        "RoundFinished",
        "MatchResultUpdated",
        "PlayerRankUpdated",
    ]
    assert websocket.sent_messages[0]["payload"]["selected_attribute"] == "speed"


@pytest.mark.anyio
async def test_play_round_publishes_realtime_events_to_match_bus() -> None:
    match = persisted_match()
    app.state.gameplay_realtime_event_bus.clear()

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        response = await client.post(
            f"/match/{match.id}/play",
            json={
                "player_card_id": str(match.player.deck_card_ids[0]),
                "opponent_card_id": str(match.opponent.deck_card_ids[0]),
                "selected_attribute": "speed",
            },
        )

    events = app.state.gameplay_realtime_event_bus.events_for_match(match.id)

    assert response.status_code == 200
    assert [event.name.value for event in events] == [
        "AttributeSelected",
        "RoundFinished",
        "MatchResultUpdated",
        "PlayerRankUpdated",
    ]
    assert events[0].payload["selected_attribute"] == "speed"
    assert events[2].payload["score"] == {"player": 0, "opponent": 0}


def test_gameplay_openapi_exposes_match_api_operations() -> None:
    openapi = app.openapi()

    assert openapi["paths"]["/match/{match_id}"]["get"]["operationId"] == "getMatchState"
    assert openapi["paths"]["/match/{match_id}/play"]["post"]["operationId"] == "playRound"
    assert openapi["paths"]["/match/{match_id}/replay"]["get"]["operationId"] == "getMatchReplay"
    assert "PlayRoundRequest" in openapi["components"]["schemas"]
    assert "MatchResponse" in openapi["components"]["schemas"]


def persisted_match():
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

    return match


async def play_first_round(match):
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        await client.post(
            f"/match/{match.id}/play",
            json={
                "player_card_id": str(match.player.deck_card_ids[0]),
                "opponent_card_id": str(match.opponent.deck_card_ids[0]),
                "selected_attribute": "speed",
            },
        )


class FakeWebSocket:
    def __init__(self, test_app):
        self.app = SimpleNamespace(state=test_app.state)
        self.accepted = False
        self.sent_messages = []

    async def accept(self):
        self.accepted = True

    async def send_json(self, payload):
        self.sent_messages.append(payload)

    async def receive_text(self):
        raise WebSocketDisconnect()


def realtime_websocket_endpoint(routes):
    for route in routes:
        endpoint = getattr(route, "endpoint", None)
        endpoint_name = getattr(endpoint, "__name__", "")
        path = getattr(route, "path", "")

        if endpoint_name == "match_events" and path.endswith("/events"):
            return endpoint

    return None


def deck_ids(prefix: str, start: int) -> tuple[UUID, ...]:
    return tuple(UUID(f"{prefix}-{index:012d}") for index in range(start, start + 10))
