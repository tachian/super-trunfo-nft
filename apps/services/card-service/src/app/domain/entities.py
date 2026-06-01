from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import UUID, uuid4

from super_trunfo_shared.cards import (
    CardAttributes,
    calculate_card_level,
    calculate_expiration_date,
)

from .exceptions import CardInvariantError

MIN_ATTRIBUTE_VALUE = 0
MAX_ATTRIBUTE_VALUE = 100


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

    def is_valid_at(self, instant: datetime) -> bool:
        return instant < self.expires_at

    def is_expired_at(self, instant: datetime) -> bool:
        return not self.is_valid_at(instant)


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
