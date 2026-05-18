from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from hashlib import sha256
from uuid import UUID

CARD_ATTRIBUTES = ("speed", "strength", "intelligence", "resistance", "rarity")


@dataclass(frozen=True)
class CardAttributes:
    name: str
    speed: int
    strength: int
    intelligence: int
    resistance: int
    rarity: int


@dataclass(frozen=True)
class Card:
    id: UUID
    nft_token_id: str
    name: str
    image_url: str
    speed: int
    strength: int
    intelligence: int
    resistance: int
    rarity: int
    family: str
    level: int
    created_at: datetime
    expires_at: datetime
    owner_id: UUID


def calculate_card_level(attributes: CardAttributes) -> int:
    return (
        attributes.speed
        + attributes.strength
        + attributes.intelligence
        + attributes.resistance
        + attributes.rarity
    )


def calculate_expiration_days(rarity: int, base_days: int = 365) -> int:
    bonus = int((rarity - 50) * 1.2)
    return base_days + bonus


def calculate_expiration_date(rarity: int, created_at: datetime | None = None) -> datetime:
    start = created_at or datetime.now(UTC)
    return start + timedelta(days=calculate_expiration_days(rarity))


def card_uniqueness_hash(attributes: CardAttributes) -> str:
    raw_value = (
        f"{attributes.name}-{attributes.speed}-{attributes.strength}-"
        f"{attributes.intelligence}-{attributes.resistance}-{attributes.rarity}"
    )
    return sha256(raw_value.encode("utf-8")).hexdigest()

