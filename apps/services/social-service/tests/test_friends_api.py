from uuid import UUID

import pytest
from app.main import app
from httpx import ASGITransport, AsyncClient

REQUESTER_ID = UUID("11111111-8010-4801-8801-000000000001")
ADDRESSEE_ID = UUID("22222222-8010-4801-8801-000000000001")
THIRD_PLAYER_ID = UUID("33333333-8010-4801-8801-000000000001")


@pytest.mark.anyio
async def test_send_accept_and_list_friendship() -> None:
    app.state.social_repository.clear()
    app.state.domain_event_publisher.clear()

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        invite_response = await client.post(
            "/friends/invite",
            json={
                "requester_id": str(REQUESTER_ID),
                "addressee_id": str(ADDRESSEE_ID),
            },
        )
        invite_id = invite_response.json()["invite"]["id"]
        accept_response = await client.post(
            f"/friends/invite/{invite_id}/accept",
            json={"player_id": str(ADDRESSEE_ID)},
        )
        friends_response = await client.get(
            "/friends",
            params={"player_id": str(REQUESTER_ID)},
        )

    accepted_payload = accept_response.json()
    friends_payload = friends_response.json()
    events = app.state.domain_event_publisher.published_events()

    assert invite_response.status_code == 201
    assert accept_response.status_code == 200
    assert friends_response.status_code == 200
    assert accepted_payload["invite"]["status"] == "accepted"
    assert accepted_payload["friendship"]["friend_id"] == str(REQUESTER_ID)
    assert friends_payload["friends"][0]["friend_id"] == str(ADDRESSEE_ID)
    assert [event.name for event in events] == ["FriendInviteSent", "FriendInviteAccepted"]


@pytest.mark.anyio
async def test_reject_friend_invite() -> None:
    app.state.social_repository.clear()
    app.state.domain_event_publisher.clear()

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        invite_response = await client.post(
            "/friends/invite",
            json={
                "requester_id": str(REQUESTER_ID),
                "addressee_id": str(THIRD_PLAYER_ID),
            },
        )
        invite_id = invite_response.json()["invite"]["id"]
        reject_response = await client.post(
            f"/friends/invite/{invite_id}/reject",
            json={"player_id": str(THIRD_PLAYER_ID)},
        )
        friends_response = await client.get(
            "/friends",
            params={"player_id": str(REQUESTER_ID)},
        )

    rejected_payload = reject_response.json()

    assert invite_response.status_code == 201
    assert reject_response.status_code == 200
    assert friends_response.json()["friends"] == []
    assert rejected_payload["invite"]["status"] == "rejected"
    assert rejected_payload["friendship"] is None
    assert app.state.domain_event_publisher.published_events()[-1].name == (
        "FriendInviteRejected"
    )


@pytest.mark.anyio
async def test_friend_invite_rejects_same_player() -> None:
    app.state.social_repository.clear()

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        response = await client.post(
            "/friends/invite",
            json={
                "requester_id": str(REQUESTER_ID),
                "addressee_id": str(REQUESTER_ID),
            },
        )

    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid friend invite."


@pytest.mark.anyio
async def test_social_routes_are_registered_in_openapi() -> None:
    paths = set(app.openapi()["paths"])

    assert "/friends" in paths
    assert "/friends/invite" in paths
    assert "/friends/invite/{invite_id}/accept" in paths
    assert "/friends/invite/{invite_id}/reject" in paths
