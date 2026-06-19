from dataclasses import dataclass
from datetime import UTC, datetime
from enum import StrEnum
from uuid import UUID, uuid4

from .exceptions import SocialInvariantError


class FriendInviteStatus(StrEnum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"


@dataclass(frozen=True)
class FriendInvite:
    id: UUID
    requester_id: UUID
    addressee_id: UUID
    status: FriendInviteStatus
    created_at: datetime
    responded_at: datetime | None = None

    def __post_init__(self) -> None:
        normalized_status = FriendInviteStatus(self.status)

        if self.requester_id == self.addressee_id:
            raise SocialInvariantError("friend invite requires different players")

        if self.created_at.tzinfo is None:
            raise SocialInvariantError("friend invite creation date must be timezone-aware")

        if self.responded_at is not None and self.responded_at.tzinfo is None:
            raise SocialInvariantError("friend invite response date must be timezone-aware")

        if normalized_status == FriendInviteStatus.PENDING and self.responded_at is not None:
            raise SocialInvariantError("pending friend invite cannot include response date")

        if normalized_status != FriendInviteStatus.PENDING and self.responded_at is None:
            raise SocialInvariantError("answered friend invite must include response date")

        object.__setattr__(self, "status", normalized_status)

    def accept(self, *, player_id: UUID, accepted_at: datetime | None = None) -> "FriendInvite":
        self._validate_response(player_id)

        return FriendInvite(
            id=self.id,
            requester_id=self.requester_id,
            addressee_id=self.addressee_id,
            status=FriendInviteStatus.ACCEPTED,
            created_at=self.created_at,
            responded_at=accepted_at or datetime.now(UTC),
        )

    def reject(self, *, player_id: UUID, rejected_at: datetime | None = None) -> "FriendInvite":
        self._validate_response(player_id)

        return FriendInvite(
            id=self.id,
            requester_id=self.requester_id,
            addressee_id=self.addressee_id,
            status=FriendInviteStatus.REJECTED,
            created_at=self.created_at,
            responded_at=rejected_at or datetime.now(UTC),
        )

    def _validate_response(self, player_id: UUID) -> None:
        if self.status != FriendInviteStatus.PENDING:
            raise SocialInvariantError("only pending friend invites can be answered")

        if player_id != self.addressee_id:
            raise SocialInvariantError("only the invite addressee can answer")


@dataclass(frozen=True)
class Friendship:
    id: UUID
    player_a_id: UUID
    player_b_id: UUID
    created_at: datetime

    def __post_init__(self) -> None:
        if self.player_a_id == self.player_b_id:
            raise SocialInvariantError("friendship requires different players")

        if self.created_at.tzinfo is None:
            raise SocialInvariantError("friendship creation date must be timezone-aware")

        player_a_id, player_b_id = sorted((self.player_a_id, self.player_b_id), key=str)

        object.__setattr__(self, "player_a_id", player_a_id)
        object.__setattr__(self, "player_b_id", player_b_id)

    def includes(self, player_id: UUID) -> bool:
        return player_id in {self.player_a_id, self.player_b_id}

    def friend_id_for(self, player_id: UUID) -> UUID:
        if player_id == self.player_a_id:
            return self.player_b_id

        if player_id == self.player_b_id:
            return self.player_a_id

        raise SocialInvariantError("player does not belong to friendship")


def create_friend_invite(
    *,
    requester_id: UUID,
    addressee_id: UUID,
    invite_id: UUID | None = None,
    created_at: datetime | None = None,
) -> FriendInvite:
    return FriendInvite(
        id=invite_id or uuid4(),
        requester_id=requester_id,
        addressee_id=addressee_id,
        status=FriendInviteStatus.PENDING,
        created_at=created_at or datetime.now(UTC),
    )


def create_friendship_from_invite(
    invite: FriendInvite,
    *,
    friendship_id: UUID | None = None,
    created_at: datetime | None = None,
) -> Friendship:
    if invite.status != FriendInviteStatus.ACCEPTED:
        raise SocialInvariantError("friendship requires accepted invite")

    return Friendship(
        id=friendship_id or uuid4(),
        player_a_id=invite.requester_id,
        player_b_id=invite.addressee_id,
        created_at=created_at or datetime.now(UTC),
    )
