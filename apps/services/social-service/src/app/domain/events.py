from super_trunfo_shared import DomainEvent

from .entities import FriendInvite, Friendship

SOCIAL_EVENT_SCHEMA_VERSION = "1.0.0"


def friend_invite_sent_event(invite: FriendInvite) -> DomainEvent:
    return DomainEvent(
        name="FriendInviteSent",
        aggregate_id=str(invite.id),
        payload=invite_payload(invite),
    )


def friend_invite_accepted_event(invite: FriendInvite, friendship: Friendship) -> DomainEvent:
    payload = invite_payload(invite)
    payload["friendship_id"] = str(friendship.id)

    return DomainEvent(
        name="FriendInviteAccepted",
        aggregate_id=str(invite.id),
        payload=payload,
    )


def friend_invite_rejected_event(invite: FriendInvite) -> DomainEvent:
    return DomainEvent(
        name="FriendInviteRejected",
        aggregate_id=str(invite.id),
        payload=invite_payload(invite),
    )


def invite_payload(invite: FriendInvite) -> dict[str, object]:
    return {
        "schema_version": SOCIAL_EVENT_SCHEMA_VERSION,
        "invite_id": str(invite.id),
        "requester_id": str(invite.requester_id),
        "addressee_id": str(invite.addressee_id),
        "status": invite.status.value,
        "created_at": invite.created_at.isoformat(),
        "responded_at": invite.responded_at.isoformat()
        if invite.responded_at is not None
        else None,
    }
