from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import UUID, uuid4

from super_trunfo_shared.cards import (
    CardAttributes,
    calculate_card_level,
    calculate_expiration_date,
    calculate_expiration_days,
    card_uniqueness_hash,
)

from .exceptions import CardInvariantError

MIN_ATTRIBUTE_VALUE = 0
MAX_ATTRIBUTE_VALUE = 100
ACTIVE_DECK_SIZE = 10


@dataclass(frozen=True)
class Card:
    id: UUID
    owner_id: UUID
    attributes: CardAttributes
    family: str
    created_at: datetime
    expires_at: datetime

    def __post_init__(self) -> None:
        validate_card_attributes(self.attributes)
        normalized_family = self.family.strip()

        if not normalized_family:
            raise CardInvariantError("card family cannot be blank")

        if self.expires_at <= self.created_at:
            raise CardInvariantError("card expiration must be after creation")

        object.__setattr__(self, "family", normalized_family)

    @property
    def name(self) -> str:
        return self.attributes.name

    @property
    def speed(self) -> int:
        return self.attributes.speed

    @property
    def strength(self) -> int:
        return self.attributes.strength

    @property
    def intelligence(self) -> int:
        return self.attributes.intelligence

    @property
    def resistance(self) -> int:
        return self.attributes.resistance

    @property
    def rarity(self) -> int:
        return self.attributes.rarity

    @property
    def level(self) -> int:
        return calculate_card_level(self.attributes)

    @property
    def uniqueness_hash(self) -> str:
        return card_uniqueness_hash(self.attributes)

    @property
    def expiration_days(self) -> int:
        return calculate_expiration_days(self.rarity)

    def is_valid_at(self, instant: datetime) -> bool:
        return instant < self.expires_at

    def is_expired_at(self, instant: datetime) -> bool:
        return not self.is_valid_at(instant)


@dataclass(frozen=True)
class Deck:
    id: UUID
    owner_id: UUID
    cards: tuple[Card, ...]
    selected_at: datetime

    def __post_init__(self) -> None:
        if len(self.cards) != ACTIVE_DECK_SIZE:
            raise CardInvariantError("active deck must contain exactly 10 cards")

        card_ids = [card.id for card in self.cards]

        if len(set(card_ids)) != ACTIVE_DECK_SIZE:
            raise CardInvariantError("active deck cannot contain duplicated cards")

        if any(card.owner_id != self.owner_id for card in self.cards):
            raise CardInvariantError("active deck cards must belong to the owner")

        if any(card.is_expired_at(self.selected_at) for card in self.cards):
            raise CardInvariantError("active deck cannot contain expired cards")

    @property
    def card_ids(self) -> tuple[UUID, ...]:
        return tuple(card.id for card in self.cards)

    @property
    def average_level(self) -> float:
        return sum(card.level for card in self.cards) / ACTIVE_DECK_SIZE


def create_card(
    *,
    owner_id: UUID,
    attributes: CardAttributes,
    family: str,
    card_id: UUID | None = None,
    created_at: datetime | None = None,
) -> Card:
    creation_time = created_at or datetime.now(UTC)

    return Card(
        id=card_id or uuid4(),
        owner_id=owner_id,
        attributes=attributes,
        family=family,
        created_at=creation_time,
        expires_at=calculate_expiration_date(attributes.rarity, creation_time),
    )


def create_deck(
    *,
    owner_id: UUID,
    cards: tuple[Card, ...],
    deck_id: UUID | None = None,
    selected_at: datetime | None = None,
) -> Deck:
    return Deck(
        id=deck_id or uuid4(),
        owner_id=owner_id,
        cards=cards,
        selected_at=selected_at or datetime.now(UTC),
    )


def validate_card_attributes(attributes: CardAttributes) -> None:
    if not attributes.name.strip():
        raise CardInvariantError("card name cannot be blank")

    numeric_attributes = (
        attributes.speed,
        attributes.strength,
        attributes.intelligence,
        attributes.resistance,
        attributes.rarity,
    )

    if any(
        value < MIN_ATTRIBUTE_VALUE or value > MAX_ATTRIBUTE_VALUE
        for value in numeric_attributes
    ):
        raise CardInvariantError("card attributes must be between 0 and 100")
