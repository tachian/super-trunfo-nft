from typing import Protocol
from uuid import UUID

from .entities import Notification


class NotificationRepository(Protocol):
    def save(self, notification: Notification) -> None:
        """Persist a notification."""

    def find_by_id(self, notification_id: UUID) -> Notification | None:
        """Find a notification by id."""

    def list_by_player_id(self, player_id: UUID) -> tuple[Notification, ...]:
        """List notifications for a player."""
