from threading import Lock
from uuid import UUID

from app.domain.entities import FriendInvite, FriendInviteStatus, Friendship


class InMemorySocialRepository:
    def __init__(self) -> None:
        self._invites_by_id: dict[UUID, FriendInvite] = {}
        self._friendships_by_pair: dict[tuple[UUID, UUID], Friendship] = {}
        self._lock = Lock()

    def save_invite(self, invite: FriendInvite) -> None:
        with self._lock:
            self._invites_by_id[invite.id] = invite

    def find_invite_by_id(self, invite_id: UUID) -> FriendInvite | None:
        return self._invites_by_id.get(invite_id)

    def find_pending_invite(self, requester_id: UUID, addressee_id: UUID) -> FriendInvite | None:
        with self._lock:
            invites = tuple(self._invites_by_id.values())

        for invite in invites:
            if (
                {invite.requester_id, invite.addressee_id}
                == {requester_id, addressee_id}
                and invite.status == FriendInviteStatus.PENDING
            ):
                return invite

        return None

    def save_friendship(self, friendship: Friendship) -> None:
        with self._lock:
            key = friendship_key(friendship.player_a_id, friendship.player_b_id)
            self._friendships_by_pair[key] = friendship

    def find_friendship(self, player_a_id: UUID, player_b_id: UUID) -> Friendship | None:
        return self._friendships_by_pair.get(friendship_key(player_a_id, player_b_id))

    def list_friendships(self, player_id: UUID) -> tuple[Friendship, ...]:
        with self._lock:
            friendships = tuple(self._friendships_by_pair.values())

        return tuple(friendship for friendship in friendships if friendship.includes(player_id))

    def clear(self) -> None:
        with self._lock:
            self._invites_by_id.clear()
            self._friendships_by_pair.clear()


def friendship_key(player_a_id: UUID, player_b_id: UUID) -> tuple[UUID, UUID]:
    return tuple(sorted((player_a_id, player_b_id), key=str))
