from dataclasses import dataclass
from typing import Protocol
from uuid import UUID, uuid4

from super_trunfo_shared.cards import CardAttributes

from app.domain.entities import Card, Deck, create_card, create_deck
from app.domain.events import card_created_event, deck_selected_event
from app.domain.exceptions import (
    CardInvariantError,
    DeckCardNotFoundError,
    DeckSelectionError,
    DuplicateCardGenerationError,
)
from app.domain.repositories import (
    CardIndexer,
    CardRepository,
    DeckRepository,
    DomainEventPublisher,
)


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


@dataclass(frozen=True)
class SelectDeckCommand:
    owner_id: UUID
    card_ids: tuple[UUID, ...]


@dataclass(frozen=True)
class SelectDeckResult:
    deck: Deck


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


class SelectDeck:
    def __init__(
        self,
        card_repository: CardRepository,
        deck_repository: DeckRepository,
        event_publisher: DomainEventPublisher,
    ) -> None:
        self.card_repository = card_repository
        self.deck_repository = deck_repository
        self.event_publisher = event_publisher

    def execute(self, command: SelectDeckCommand) -> SelectDeckResult:
        if len(command.card_ids) != 10:
            raise DeckSelectionError("active deck must contain exactly 10 cards")

        if len(set(command.card_ids)) != len(command.card_ids):
            raise DeckSelectionError("active deck cannot contain duplicated cards")

        cards = tuple(
            self._find_owned_card(command.owner_id, card_id)
            for card_id in command.card_ids
        )

        try:
            deck = create_deck(owner_id=command.owner_id, cards=cards)
        except CardInvariantError as exc:
            raise DeckSelectionError(str(exc)) from exc

        self.deck_repository.save(deck)
        self.event_publisher.publish(deck_selected_event(deck))

        return SelectDeckResult(deck=deck)

    def _find_owned_card(self, owner_id: UUID, card_id: UUID) -> Card:
        card = self.card_repository.find_by_id(card_id)

        if card is None:
            raise DeckCardNotFoundError("selected card was not found")

        if card.owner_id != owner_id:
            raise DeckSelectionError("selected card does not belong to the owner")

        return card
