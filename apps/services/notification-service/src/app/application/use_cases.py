from dataclasses import dataclass, field
from typing import Protocol
from uuid import UUID

from super_trunfo_shared import DomainEvent

from app.domain.entities import (
    Notification,
    NotificationChannel,
    NotificationTopic,
    notification_from_external_event,
    queue_notification,
)
from app.domain.events import notification_delivered_event, notification_queued_event
from app.domain.exceptions import NotificationNotFoundError
from app.domain.repositories import NotificationRepository


class DomainEventPublisher(Protocol):
    def publish(self, event: DomainEvent) -> None:
        """Publish a domain event."""


@dataclass(frozen=True)
class QueueNotificationCommand:
    player_id: UUID
    topic: NotificationTopic
    channel: NotificationChannel
    title: str
    message: str
    source_event_id: str | None = None
    metadata: dict[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class QueueNotificationFromEventCommand:
    name: str
    payload: dict[str, object]
    event_id: str | None = None
    channel: NotificationChannel = NotificationChannel.IN_APP


@dataclass(frozen=True)
class MarkNotificationDeliveredCommand:
    notification_id: UUID


@dataclass(frozen=True)
class ListNotificationsQuery:
    player_id: UUID


@dataclass(frozen=True)
class NotificationResult:
    notification: Notification
    events: tuple[DomainEvent, ...] = ()


@dataclass(frozen=True)
class ListNotificationsResult:
    player_id: UUID
    notifications: tuple[Notification, ...]


class QueueNotification:
    def __init__(
        self,
        repository: NotificationRepository,
        event_publisher: DomainEventPublisher,
    ) -> None:
        self.repository = repository
        self.event_publisher = event_publisher

    def execute(self, command: QueueNotificationCommand) -> NotificationResult:
        notification = queue_notification(
            player_id=command.player_id,
            topic=command.topic,
            channel=command.channel,
            title=command.title,
            message=command.message,
            source_event_id=command.source_event_id,
            metadata=command.metadata,
        )
        return self._persist_and_publish(notification)

    def _persist_and_publish(self, notification: Notification) -> NotificationResult:
        self.repository.save(notification)

        event = notification_queued_event(notification)
        self.event_publisher.publish(event)

        return NotificationResult(notification=notification, events=(event,))


class QueueNotificationFromEvent:
    def __init__(
        self,
        repository: NotificationRepository,
        event_publisher: DomainEventPublisher,
    ) -> None:
        self.repository = repository
        self.event_publisher = event_publisher

    def execute(self, command: QueueNotificationFromEventCommand) -> NotificationResult:
        notification = notification_from_external_event(
            name=command.name,
            payload=command.payload,
            event_id=command.event_id,
            channel=command.channel,
        )
        self.repository.save(notification)

        event = notification_queued_event(notification)
        self.event_publisher.publish(event)

        return NotificationResult(notification=notification, events=(event,))


class MarkNotificationDelivered:
    def __init__(
        self,
        repository: NotificationRepository,
        event_publisher: DomainEventPublisher,
    ) -> None:
        self.repository = repository
        self.event_publisher = event_publisher

    def execute(self, command: MarkNotificationDeliveredCommand) -> NotificationResult:
        notification = self.repository.find_by_id(command.notification_id)

        if notification is None:
            raise NotificationNotFoundError("notification was not found")

        delivered_notification = notification.mark_delivered()
        self.repository.save(delivered_notification)

        event = notification_delivered_event(delivered_notification)
        self.event_publisher.publish(event)

        return NotificationResult(notification=delivered_notification, events=(event,))


class ListNotifications:
    def __init__(self, repository: NotificationRepository) -> None:
        self.repository = repository

    def execute(self, query: ListNotificationsQuery) -> ListNotificationsResult:
        return ListNotificationsResult(
            player_id=query.player_id,
            notifications=self.repository.list_by_player_id(query.player_id),
        )
