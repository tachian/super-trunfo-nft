from threading import Lock
from uuid import UUID

from app.domain.entities import Notification


class InMemoryNotificationRepository:
    def __init__(self) -> None:
        self._notifications_by_id: dict[UUID, Notification] = {}
        self._lock = Lock()

    def save(self, notification: Notification) -> None:
        with self._lock:
            self._notifications_by_id[notification.id] = notification

    def find_by_id(self, notification_id: UUID) -> Notification | None:
        return self._notifications_by_id.get(notification_id)

    def list_by_player_id(self, player_id: UUID) -> tuple[Notification, ...]:
        with self._lock:
            notifications = tuple(self._notifications_by_id.values())

        return tuple(
            sorted(
                (
                    notification
                    for notification in notifications
                    if notification.player_id == player_id
                ),
                key=lambda notification: notification.created_at,
                reverse=True,
            )
        )

    def clear(self) -> None:
        with self._lock:
            self._notifications_by_id.clear()
