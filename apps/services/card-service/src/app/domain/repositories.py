from dataclasses import dataclass
from datetime import datetime
from typing import Protocol
from uuid import UUID

from super_trunfo_shared import DomainEvent

from .entities import Card


@dataclass(frozen=True)
class CardSearchDocument:
    card_id: UUID
    owner_id: UUID
    name: str
    family: str
    rarity: int
    level: int
    expires_at: datetime
    uniqueness_hash: str
    generation_batch_id: UUID


class DomainEventPublisher(Protocol):
    def publish(self, event: DomainEvent) -> None:
        """Publish a domain event to the platform event bus."""


class CardIndexer(Protocol):
    def index(self, card: Card, generation_batch_id: UUID) -> None:
        """Index a generated card for basic search use cases."""

    def find_by_owner(self, owner_id: UUID) -> tuple[CardSearchDocument, ...]:
        """Find indexed cards by owner."""


class CardRepository(Protocol):
    def add(self, card: Card) -> None:
        """Persist a new card aggregate."""

    def exists_by_uniqueness_hash(self, uniqueness_hash: str) -> bool:
        """Return whether an identical card already exists."""

    def find_by_id(self, card_id: UUID) -> Card | None:
        """Find a card by id."""
