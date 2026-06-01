from typing import Protocol
from uuid import UUID

from .entities import Player


class PlayerRepository(Protocol):
    def add(self, player: Player) -> None:
        """Persist a new player."""

    def find_by_email(self, email: str) -> Player | None:
        """Find a player by normalized email."""

    def find_by_nickname(self, nickname: str) -> Player | None:
        """Find a player by normalized nickname."""

    def find_by_id(self, player_id: UUID) -> Player | None:
        """Find a player by id."""
