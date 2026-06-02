from dataclasses import dataclass
from typing import Protocol
from uuid import UUID

from super_trunfo_shared.cards import CardAttributes

from app.domain.entities import Card, create_card
from app.domain.exceptions import DuplicateCardGenerationError
from app.domain.repositories import CardRepository


class CardAttributeGenerator(Protocol):
    def generate(self) -> CardAttributes:
        """Generate candidate card attributes."""


@dataclass(frozen=True)
class GenerateUniqueCardCommand:
    owner_id: UUID
    family: str


@dataclass(frozen=True)
class GenerateUniqueCardResult:
    card: Card
    attempts: int


class GenerateUniqueCard:
    def __init__(
        self,
        repository: CardRepository,
        attribute_generator: CardAttributeGenerator,
        max_attempts: int = 5,
    ) -> None:
        self.repository = repository
        self.attribute_generator = attribute_generator
        self.max_attempts = max_attempts

    def execute(self, command: GenerateUniqueCardCommand) -> GenerateUniqueCardResult:
        for attempt in range(1, self.max_attempts + 1):
            card = create_card(
                owner_id=command.owner_id,
                attributes=self.attribute_generator.generate(),
                family=command.family,
            )

            if self.repository.exists_by_uniqueness_hash(card.uniqueness_hash):
                continue

            self.repository.add(card)
            return GenerateUniqueCardResult(card=card, attempts=attempt)

        raise DuplicateCardGenerationError("could not generate a unique card")
