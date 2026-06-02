from dataclasses import dataclass
from typing import Protocol
from uuid import UUID, uuid4

from super_trunfo_shared.cards import CardAttributes

from app.domain.entities import Card, create_card
from app.domain.events import card_created_event
from app.domain.exceptions import DuplicateCardGenerationError
from app.domain.repositories import CardIndexer, CardRepository, DomainEventPublisher


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


@dataclass(frozen=True)
class GenerateProceduralCardsCommand:
    owner_id: UUID
    family: str
    quantity: int
    generation_batch_id: UUID | None = None


@dataclass(frozen=True)
class GenerateProceduralCardsResult:
    generation_batch_id: UUID
    cards: tuple[Card, ...]
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


class GenerateProceduralCards:
    def __init__(
        self,
        repository: CardRepository,
        attribute_generator: CardAttributeGenerator,
        card_indexer: CardIndexer,
        event_publisher: DomainEventPublisher,
        max_attempts_per_card: int = 5,
    ) -> None:
        self.repository = repository
        self.attribute_generator = attribute_generator
        self.card_indexer = card_indexer
        self.event_publisher = event_publisher
        self.max_attempts_per_card = max_attempts_per_card

    def execute(self, command: GenerateProceduralCardsCommand) -> GenerateProceduralCardsResult:
        if command.quantity <= 0:
            raise ValueError("generation quantity must be greater than zero")

        batch_id = command.generation_batch_id or uuid4()
        cards: list[Card] = []
        total_attempts = 0
        generate_unique_card = GenerateUniqueCard(
            self.repository,
            self.attribute_generator,
            max_attempts=self.max_attempts_per_card,
        )

        for _ in range(command.quantity):
            result = generate_unique_card.execute(
                GenerateUniqueCardCommand(
                    owner_id=command.owner_id,
                    family=command.family,
                )
            )
            total_attempts += result.attempts
            cards.append(result.card)

            self.card_indexer.index(result.card, batch_id)
            self.event_publisher.publish(card_created_event(result.card, batch_id))

        return GenerateProceduralCardsResult(
            generation_batch_id=batch_id,
            cards=tuple(cards),
            attempts=total_attempts,
        )
