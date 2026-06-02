from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from hashlib import sha256
from json import dumps

CARD_ATTRIBUTES = ("speed", "strength", "intelligence", "resistance", "rarity")
BASE_EXPIRATION_DAYS = 365
RARITY_EXPIRATION_PIVOT = 50
RARITY_EXPIRATION_MULTIPLIER = 1.2


@dataclass(frozen=True)
class CardAttributes:
    name: str
    speed: int
    strength: int
    intelligence: int
    resistance: int
    rarity: int


def calculate_card_level(attributes: CardAttributes) -> int:
    return (
        attributes.speed
        + attributes.strength
        + attributes.intelligence
        + attributes.resistance
        + attributes.rarity
    )


def calculate_expiration_bonus_days(rarity: int) -> int:
    return int((rarity - RARITY_EXPIRATION_PIVOT) * RARITY_EXPIRATION_MULTIPLIER)


def calculate_expiration_days(rarity: int, base_days: int = BASE_EXPIRATION_DAYS) -> int:
    return base_days + calculate_expiration_bonus_days(rarity)


def calculate_expiration_date(rarity: int, created_at: datetime | None = None) -> datetime:
    start = created_at or datetime.now(UTC)
    return start + timedelta(days=calculate_expiration_days(rarity))


def card_uniqueness_hash(attributes: CardAttributes) -> str:
    canonical_payload = dumps(
        {
            "intelligence": attributes.intelligence,
            "name": attributes.name.strip().lower(),
            "rarity": attributes.rarity,
            "resistance": attributes.resistance,
            "speed": attributes.speed,
            "strength": attributes.strength,
        },
        separators=(",", ":"),
        sort_keys=True,
    )
    return sha256(canonical_payload.encode("utf-8")).hexdigest()
