from uuid import UUID

import pytest
from app.application.use_cases import (
    ListNotifications,
    ListNotificationsQuery,
    MarkNotificationDelivered,
    MarkNotificationDeliveredCommand,
    QueueNotification,
    QueueNotificationCommand,
    QueueNotificationFromEvent,
    QueueNotificationFromEventCommand,
)
from app.domain.entities import (
    NotificationChannel,
    NotificationStatus,
    NotificationTopic,
    queue_notification,
)
from app.domain.exceptions import NotificationInvariantError, UnsupportedNotificationEventError
from app.infrastructure.repositories import InMemoryNotificationRepository
from super_trunfo_shared import InMemoryDomainEventPublisher

PLAYER_ID = UUID("11111111-8020-4802-8802-000000000001")
FRIEND_ID = UUID("22222222-8020-4802-8802-000000000001")
NOTIFICATION_ID = UUID("33333333-8020-4802-8802-000000000001")


def test_queue_notification_persists_and_publishes_event() -> None:
    repository = InMemoryNotificationRepository()
    event_publisher = InMemoryDomainEventPublisher(
        service_name="notification-service",
        context="notification",
    )
    use_case = QueueNotification(repository, event_publisher)

    result = use_case.execute(
        QueueNotificationCommand(
            player_id=PLAYER_ID,
            topic=NotificationTopic.INVITE,
            channel=NotificationChannel.PUSH,
            title="Novo convite",
            message="Voce recebeu um convite.",
            metadata={"origin": "test"},
        )
    )

    notifications = ListNotifications(repository).execute(
        ListNotificationsQuery(player_id=PLAYER_ID)
    )
    events = event_publisher.published_events()

    assert notifications.notifications == (result.notification,)
    assert result.notification.status == NotificationStatus.QUEUED
    assert events[0].name == "NotificationQueued"
    assert events[0].payload["notification_id"] == str(result.notification.id)
    assert events[0].payload["channel"] == "push"


def test_notification_requires_title_and_message() -> None:
    with pytest.raises(NotificationInvariantError, match="title"):
        queue_notification(
            player_id=PLAYER_ID,
            topic=NotificationTopic.EVENT,
            channel=NotificationChannel.IN_APP,
            title=" ",
            message="Evento importante.",
        )

    with pytest.raises(NotificationInvariantError, match="message"):
        queue_notification(
            player_id=PLAYER_ID,
            topic=NotificationTopic.EVENT,
            channel=NotificationChannel.IN_APP,
            title="Evento",
            message=" ",
        )


def test_mark_notification_delivered_updates_status_and_publishes_event() -> None:
    repository = InMemoryNotificationRepository()
    event_publisher = InMemoryDomainEventPublisher(
        service_name="notification-service",
        context="notification",
    )
    notification = queue_notification(
        player_id=PLAYER_ID,
        topic=NotificationTopic.MATCH,
        channel=NotificationChannel.IN_APP,
        title="Partida encontrada",
        message="Sua partida esta pronta.",
        notification_id=NOTIFICATION_ID,
    )
    repository.save(notification)

    result = MarkNotificationDelivered(repository, event_publisher).execute(
        MarkNotificationDeliveredCommand(notification_id=NOTIFICATION_ID)
    )

    events = event_publisher.published_events()

    assert result.notification.status == NotificationStatus.DELIVERED
    assert result.notification.delivered_at is not None
    assert repository.find_by_id(NOTIFICATION_ID) == result.notification
    assert events[0].name == "NotificationDelivered"


def test_queue_notification_from_friend_invite_event_targets_addressee() -> None:
    repository = InMemoryNotificationRepository()
    event_publisher = InMemoryDomainEventPublisher(
        service_name="notification-service",
        context="notification",
    )

    result = QueueNotificationFromEvent(repository, event_publisher).execute(
        QueueNotificationFromEventCommand(
            name="FriendInviteSent",
            event_id="event-802",
            payload={
                "invite_id": "44444444-8020-4802-8802-000000000001",
                "requester_id": str(FRIEND_ID),
                "addressee_id": str(PLAYER_ID),
            },
        )
    )

    assert result.notification.player_id == PLAYER_ID
    assert result.notification.topic == NotificationTopic.INVITE
    assert result.notification.source_event_id == "event-802"
    assert result.notification.metadata["event_name"] == "FriendInviteSent"


@pytest.mark.parametrize(
    ("event_name", "payload", "topic"),
    [
        (
            "MatchStarted",
            {"player_id": str(PLAYER_ID), "match_id": str(FRIEND_ID)},
            NotificationTopic.MATCH,
        ),
        (
            "OfferPurchased",
            {"player_id": str(PLAYER_ID), "offer_id": str(FRIEND_ID)},
            NotificationTopic.SHOP,
        ),
        (
            "PlayerRankUpdated",
            {"player_id": str(PLAYER_ID), "score": 1200},
            NotificationTopic.RANKING,
        ),
        (
            "CustomEvent",
            {"player_id": str(PLAYER_ID), "source": "test"},
            NotificationTopic.EVENT,
        ),
    ],
)
def test_queue_notification_from_supported_events(
    event_name: str,
    payload: dict[str, object],
    topic: NotificationTopic,
) -> None:
    repository = InMemoryNotificationRepository()
    event_publisher = InMemoryDomainEventPublisher(
        service_name="notification-service",
        context="notification",
    )

    result = QueueNotificationFromEvent(repository, event_publisher).execute(
        QueueNotificationFromEventCommand(name=event_name, payload=payload)
    )

    assert result.notification.player_id == PLAYER_ID
    assert result.notification.topic == topic
    assert event_publisher.published_events()[0].name == "NotificationQueued"


def test_queue_notification_from_event_rejects_missing_recipient() -> None:
    repository = InMemoryNotificationRepository()
    event_publisher = InMemoryDomainEventPublisher(
        service_name="notification-service",
        context="notification",
    )

    with pytest.raises(UnsupportedNotificationEventError, match="recipient"):
        QueueNotificationFromEvent(repository, event_publisher).execute(
            QueueNotificationFromEventCommand(
                name="UnknownEvent",
                payload={"status": "ignored"},
            )
        )
