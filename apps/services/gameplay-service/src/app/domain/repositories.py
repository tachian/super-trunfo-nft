from typing import Protocol
from uuid import UUID

from .entities import GameplayRealtimeEvent, Match


class MatchRepository(Protocol):
    def save(self, match: Match) -> None:
        """Persist match state."""

    def find_by_id(self, match_id: UUID) -> Match | None:
        """Find match state by id."""


class GameplayRealtimePublisher(Protocol):
    def publish(self, event: GameplayRealtimeEvent) -> None:
        """Publish a realtime gameplay event."""
