from datetime import UTC, datetime
from uuid import UUID

import pytest
from app.application.use_cases import (
    AcceptFriendInvite,
    AnswerFriendInviteCommand,
    ListFriends,
    ListFriendsQuery,
    RejectFriendInvite,
    SendFriendInvite,
    SendFriendInviteCommand,
)
from app.domain.entities import FriendInviteStatus, create_friend_invite
from app.domain.exceptions import SocialInvariantError
from app.infrastructure.repositories import InMemorySocialRepository
from super_trunfo_shared import InMemoryDomainEventPublisher

REQUESTER_ID = UUID("11111111-8010-4801-8801-000000000001")
ADDRESSEE_ID = UUID("22222222-8010-4801-8801-000000000001")
THIRD_PLAYER_ID = UUID("33333333-8010-4801-8801-000000000001")


def test_friend_invite_requires_different_players() -> None:
    with pytest.raises(SocialInvariantError, match="different players"):
        create_friend_invite(
            requester_id=REQUESTER_ID,
            addressee_id=REQUESTER_ID,
        )


def test_send_friend_invite_persists_and_publishes_event() -> None:
    repository = InMemorySocialRepository()
    event_publisher = InMemoryDomainEventPublisher(service_name="social-service", context="social")
    use_case = SendFriendInvite(repository, event_publisher)

    result = use_case.execute(
        SendFriendInviteCommand(
            requester_id=REQUESTER_ID,
            addressee_id=ADDRESSEE_ID,
        )
    )

    events = event_publisher.published_events()

    assert repository.find_invite_by_id(result.invite.id) == result.invite
    assert result.invite.status == FriendInviteStatus.PENDING
    assert len(events) == 1
    assert events[0].name == "FriendInviteSent"
    assert events[0].payload["invite_id"] == str(result.invite.id)


def test_send_friend_invite_rejects_duplicate_pending_invite() -> None:
    repository = InMemorySocialRepository()
    event_publisher = InMemoryDomainEventPublisher(service_name="social-service", context="social")
    use_case = SendFriendInvite(repository, event_publisher)
    command = SendFriendInviteCommand(
        requester_id=REQUESTER_ID,
        addressee_id=ADDRESSEE_ID,
    )
    use_case.execute(command)

    with pytest.raises(SocialInvariantError, match="already pending"):
        use_case.execute(command)

    with pytest.raises(SocialInvariantError, match="already pending"):
        use_case.execute(
            SendFriendInviteCommand(
                requester_id=ADDRESSEE_ID,
                addressee_id=REQUESTER_ID,
            )
        )


def test_accept_friend_invite_creates_friendship_and_event() -> None:
    repository = InMemorySocialRepository()
    event_publisher = InMemoryDomainEventPublisher(service_name="social-service", context="social")
    invite = create_friend_invite(
        requester_id=REQUESTER_ID,
        addressee_id=ADDRESSEE_ID,
        created_at=datetime(2026, 6, 19, 10, 0, tzinfo=UTC),
    )
    repository.save_invite(invite)
    use_case = AcceptFriendInvite(repository, event_publisher)

    result = use_case.execute(
        AnswerFriendInviteCommand(
            invite_id=invite.id,
            player_id=ADDRESSEE_ID,
        )
    )

    friendships = ListFriends(repository).execute(ListFriendsQuery(player_id=REQUESTER_ID))
    events = event_publisher.published_events()

    assert result.invite.status == FriendInviteStatus.ACCEPTED
    assert result.friendship is not None
    assert friendships.friendships == (result.friendship,)
    assert events[0].name == "FriendInviteAccepted"
    assert events[0].payload["friendship_id"] == str(result.friendship.id)


def test_reject_friend_invite_does_not_create_friendship() -> None:
    repository = InMemorySocialRepository()
    event_publisher = InMemoryDomainEventPublisher(service_name="social-service", context="social")
    invite = create_friend_invite(requester_id=REQUESTER_ID, addressee_id=ADDRESSEE_ID)
    repository.save_invite(invite)
    use_case = RejectFriendInvite(repository, event_publisher)

    result = use_case.execute(
        AnswerFriendInviteCommand(
            invite_id=invite.id,
            player_id=ADDRESSEE_ID,
        )
    )

    friendships = ListFriends(repository).execute(ListFriendsQuery(player_id=REQUESTER_ID))
    events = event_publisher.published_events()

    assert result.invite.status == FriendInviteStatus.REJECTED
    assert result.friendship is None
    assert friendships.friendships == ()
    assert events[0].name == "FriendInviteRejected"


def test_only_invite_addressee_can_answer() -> None:
    invite = create_friend_invite(requester_id=REQUESTER_ID, addressee_id=ADDRESSEE_ID)

    with pytest.raises(SocialInvariantError, match="addressee"):
        invite.accept(player_id=THIRD_PLAYER_ID)
