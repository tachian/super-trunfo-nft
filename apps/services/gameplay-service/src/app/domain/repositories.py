from typing import Protocol
from uuid import UUID

from .entities import Match


class MatchRepository(Protocol):
    def save(self, match: Match) -> None:
        """Persist match state."""

    def find_by_id(self, match_id: UUID) -> Match | None:
        """Find match state by id."""
