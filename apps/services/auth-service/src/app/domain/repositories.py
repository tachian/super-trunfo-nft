from typing import Protocol
from uuid import UUID

from super_trunfo_shared import DomainEvent

from .entities import Player


class DomainEventPublisher(Protocol):
    def publish(self, event: DomainEvent) -> None:
        """Publish a domain event to the platform event bus."""


class PlayerRepository(Protocol):
    def add(self, player: Player) -> None:
        """Persist a new player."""

    def save(self, player: Player) -> None:
        """Persist changes to an existing player aggregate."""

    def find_by_email(self, email: str) -> Player | None:
        """Find a player by normalized email."""

    def find_by_nickname(self, nickname: str) -> Player | None:
        """Find a player by normalized nickname."""

    def find_by_id(self, player_id: UUID) -> Player | None:
        """Find a player by id."""
