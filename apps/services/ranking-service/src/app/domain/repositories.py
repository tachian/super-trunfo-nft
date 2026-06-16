from typing import Protocol
from uuid import UUID

from super_trunfo_shared import DomainEvent

from .entities import Rating


class RatingRepository(Protocol):
    def save_many(self, ratings: tuple[Rating, ...]) -> None:
        """Persist player ratings atomically."""

    def find_by_player_id(self, player_id: UUID) -> Rating | None:
        """Find a rating by player id."""


class DomainEventPublisher(Protocol):
    def publish(self, event: DomainEvent) -> None:
        """Publish a domain event."""
