from typing import Protocol
from uuid import UUID

from super_trunfo_shared import DomainEvent

from .entities import LeaderboardEntry, Rating


class RatingRepository(Protocol):
    def save_many(self, ratings: tuple[Rating, ...]) -> None:
        """Persist player ratings atomically."""

    def find_by_player_id(self, player_id: UUID) -> Rating | None:
        """Find a rating by player id."""

    def list_all(self) -> tuple[Rating, ...]:
        """List all persisted ratings."""

    def version(self) -> int:
        """Return a monotonically increasing repository version."""


class LeaderboardCache(Protocol):
    def get(self, key: str) -> tuple[LeaderboardEntry, ...] | None:
        """Return cached leaderboard entries for a key."""

    def set(self, key: str, entries: tuple[LeaderboardEntry, ...]) -> None:
        """Cache leaderboard entries for a key."""


class DomainEventPublisher(Protocol):
    def publish(self, event: DomainEvent) -> None:
        """Publish a domain event."""
