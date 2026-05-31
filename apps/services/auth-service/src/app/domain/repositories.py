from typing import Protocol

from .entities import Player


class PlayerRepository(Protocol):
    def add(self, player: Player) -> None:
        """Persist a new player."""

    def find_by_email(self, email: str) -> Player | None:
        """Find a player by normalized email."""

    def find_by_nickname(self, nickname: str) -> Player | None:
        """Find a player by normalized nickname."""
