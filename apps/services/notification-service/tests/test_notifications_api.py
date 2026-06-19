from uuid import UUID

import pytest
from app.main import app
from httpx import ASGITransport, AsyncClient

PLAYER_ID = UUID("11111111-8020-4802-8802-000000000001")
FRIEND_ID = UUID("22222222-8020-4802-8802-000000000001")


@pytest.mark.anyio
async def test_queue_list_and_deliver_notification() -> None:
    app.state.notification_repository.clear()
    app.state.domain_event_publisher.clear()

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        queue_response = await client.post(
            "/notifications/push",
            json={
                "player_id": str(PLAYER_ID),
                "topic": "match",
                "channel": "push",
                "title": "Partida encontrada",
                "message": "Sua partida esta pronta.",
                "metadata": {"mode": "pvp"},
            },
        )
        notification_id = queue_response.json()["notification"]["id"]
        delivered_response = await client.post(
            f"/notifications/{notification_id}/delivered"
        )
        list_response = await client.get(
            "/notifications",
            params={"player_id": str(PLAYER_ID)},
        )

    listed_notification = list_response.json()["notifications"][0]
    events = app.state.domain_event_publisher.published_events()

    assert queue_response.status_code == 201
    assert delivered_response.status_code == 200
    assert list_response.status_code == 200
    assert listed_notification["status"] == "delivered"
    assert listed_notification["channel"] == "push"
    assert [event.name for event in events] == [
        "NotificationQueued",
        "NotificationDelivered",
    ]


@pytest.mark.anyio
async def test_queue_notification_from_friend_invite_event() -> None:
    app.state.notification_repository.clear()
    app.state.domain_event_publisher.clear()

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        response = await client.post(
            "/notifications/events",
            json={
                "name": "FriendInviteSent",
                "event_id": "event-802",
                "payload": {
                    "invite_id": "44444444-8020-4802-8802-000000000001",
                    "requester_id": str(FRIEND_ID),
                    "addressee_id": str(PLAYER_ID),
                },
            },
        )
        list_response = await client.get(
            "/notifications",
            params={"player_id": str(PLAYER_ID)},
        )

    notification = response.json()["notification"]

    assert response.status_code == 201
    assert list_response.status_code == 200
    assert notification["topic"] == "invite"
    assert notification["player_id"] == str(PLAYER_ID)
    assert notification["metadata"]["event_name"] == "FriendInviteSent"
    assert len(list_response.json()["notifications"]) == 1


@pytest.mark.anyio
async def test_notification_event_rejects_payload_without_recipient() -> None:
    app.state.notification_repository.clear()

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        response = await client.post(
            "/notifications/events",
            json={
                "name": "UnknownEvent",
                "payload": {"status": "ignored"},
            },
        )

    assert response.status_code == 400
    assert response.json()["detail"] == "Unsupported notification event."


@pytest.mark.anyio
async def test_notification_routes_are_registered_in_openapi() -> None:
    paths = set(app.openapi()["paths"])

    assert "/notifications" in paths
    assert "/notifications/push" in paths
    assert "/notifications/events" in paths
    assert "/notifications/{notification_id}/delivered" in paths
