from super_trunfo_shared import DomainEvent

from .entities import Notification

NOTIFICATION_EVENT_SCHEMA_VERSION = "1.0.0"


def notification_queued_event(notification: Notification) -> DomainEvent:
    return DomainEvent(
        name="NotificationQueued",
        aggregate_id=str(notification.id),
        payload=notification_payload(notification),
    )


def notification_delivered_event(notification: Notification) -> DomainEvent:
    return DomainEvent(
        name="NotificationDelivered",
        aggregate_id=str(notification.id),
        payload=notification_payload(notification),
    )


def notification_payload(notification: Notification) -> dict[str, object]:
    return {
        "schema_version": NOTIFICATION_EVENT_SCHEMA_VERSION,
        "notification_id": str(notification.id),
        "player_id": str(notification.player_id),
        "topic": notification.topic.value,
        "channel": notification.channel.value,
        "status": notification.status.value,
        "title": notification.title,
        "source_event_id": notification.source_event_id,
        "created_at": notification.created_at.isoformat(),
        "delivered_at": notification.delivered_at.isoformat()
        if notification.delivered_at is not None
        else None,
    }
