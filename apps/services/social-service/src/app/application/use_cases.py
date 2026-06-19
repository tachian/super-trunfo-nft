from dataclasses import dataclass
from typing import Protocol
from uuid import UUID

from super_trunfo_shared import DomainEvent

from app.domain.entities import (
    FriendInvite,
    Friendship,
    create_friend_invite,
    create_friendship_from_invite,
)
from app.domain.events import (
    friend_invite_accepted_event,
    friend_invite_rejected_event,
    friend_invite_sent_event,
)
from app.domain.exceptions import FriendInviteNotFoundError, SocialInvariantError
from app.domain.repositories import SocialRepository


class DomainEventPublisher(Protocol):
    def publish(self, event: DomainEvent) -> None:
        """Publish a domain event."""


@dataclass(frozen=True)
class SendFriendInviteCommand:
    requester_id: UUID
    addressee_id: UUID


@dataclass(frozen=True)
class AnswerFriendInviteCommand:
    invite_id: UUID
    player_id: UUID


@dataclass(frozen=True)
class ListFriendsQuery:
    player_id: UUID


@dataclass(frozen=True)
class FriendInviteResult:
    invite: FriendInvite
    friendship: Friendship | None = None
    events: tuple[DomainEvent, ...] = ()


@dataclass(frozen=True)
class ListFriendsResult:
    player_id: UUID
    friendships: tuple[Friendship, ...]


class SendFriendInvite:
    def __init__(
        self,
        repository: SocialRepository,
        event_publisher: DomainEventPublisher,
    ) -> None:
        self.repository = repository
        self.event_publisher = event_publisher

    def execute(self, command: SendFriendInviteCommand) -> FriendInviteResult:
        if self.repository.find_friendship(command.requester_id, command.addressee_id) is not None:
            raise SocialInvariantError("players are already friends")

        if (
            self.repository.find_pending_invite(command.requester_id, command.addressee_id)
            is not None
        ):
            raise SocialInvariantError("friend invite is already pending")

        invite = create_friend_invite(
            requester_id=command.requester_id,
            addressee_id=command.addressee_id,
        )
        self.repository.save_invite(invite)

        event = friend_invite_sent_event(invite)
        self.event_publisher.publish(event)

        return FriendInviteResult(invite=invite, events=(event,))


class AcceptFriendInvite:
    def __init__(
        self,
        repository: SocialRepository,
        event_publisher: DomainEventPublisher,
    ) -> None:
        self.repository = repository
        self.event_publisher = event_publisher

    def execute(self, command: AnswerFriendInviteCommand) -> FriendInviteResult:
        invite = self.repository.find_invite_by_id(command.invite_id)

        if invite is None:
            raise FriendInviteNotFoundError("friend invite was not found")

        accepted_invite = invite.accept(player_id=command.player_id)
        friendship = create_friendship_from_invite(accepted_invite)
        self.repository.save_invite(accepted_invite)
        self.repository.save_friendship(friendship)

        event = friend_invite_accepted_event(accepted_invite, friendship)
        self.event_publisher.publish(event)

        return FriendInviteResult(
            invite=accepted_invite,
            friendship=friendship,
            events=(event,),
        )


class RejectFriendInvite:
    def __init__(
        self,
        repository: SocialRepository,
        event_publisher: DomainEventPublisher,
    ) -> None:
        self.repository = repository
        self.event_publisher = event_publisher

    def execute(self, command: AnswerFriendInviteCommand) -> FriendInviteResult:
        invite = self.repository.find_invite_by_id(command.invite_id)

        if invite is None:
            raise FriendInviteNotFoundError("friend invite was not found")

        rejected_invite = invite.reject(player_id=command.player_id)
        self.repository.save_invite(rejected_invite)

        event = friend_invite_rejected_event(rejected_invite)
        self.event_publisher.publish(event)

        return FriendInviteResult(invite=rejected_invite, events=(event,))


class ListFriends:
    def __init__(self, repository: SocialRepository) -> None:
        self.repository = repository

    def execute(self, query: ListFriendsQuery) -> ListFriendsResult:
        return ListFriendsResult(
            player_id=query.player_id,
            friendships=self.repository.list_friendships(query.player_id),
        )
