from uuid import UUID

from super_trunfo_shared import DomainEvent

from .entities import Card

CARD_EVENT_SCHEMA_VERSION = "1.0.0"


def card_created_event(card: Card, generation_batch_id: UUID) -> DomainEvent:
    return DomainEvent(
        name="CardCreated",
        aggregate_id=str(card.id),
        payload={
            "schema_version": CARD_EVENT_SCHEMA_VERSION,
            "card_id": str(card.id),
            "owner_id": str(card.owner_id),
            "name": card.name,
            "family": card.family,
            "rarity": card.rarity,
            "level": card.level,
            "uniqueness_hash": card.uniqueness_hash,
            "expires_at": card.expires_at.isoformat(),
            "generation_batch_id": str(generation_batch_id),
        },
    )
