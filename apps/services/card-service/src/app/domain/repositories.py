from typing import Protocol
from uuid import UUID

from .entities import Card


class CardRepository(Protocol):
    def add(self, card: Card) -> None:
        """Persist a new card aggregate."""

    def exists_by_uniqueness_hash(self, uniqueness_hash: str) -> bool:
        """Return whether an identical card already exists."""

    def find_by_id(self, card_id: UUID) -> Card | None:
        """Find a card by id."""
