from typing import Protocol
from uuid import UUID

from .entities import FriendInvite, Friendship


class SocialRepository(Protocol):
    def save_invite(self, invite: FriendInvite) -> None:
        """Persist a friend invite."""

    def find_invite_by_id(self, invite_id: UUID) -> FriendInvite | None:
        """Find a friend invite by id."""

    def find_pending_invite(self, requester_id: UUID, addressee_id: UUID) -> FriendInvite | None:
        """Find a pending invite between requester and addressee."""

    def save_friendship(self, friendship: Friendship) -> None:
        """Persist a friendship."""

    def find_friendship(self, player_a_id: UUID, player_b_id: UUID) -> Friendship | None:
        """Find a friendship between two players."""

    def list_friendships(self, player_id: UUID) -> tuple[Friendship, ...]:
        """List friendships for a player."""
