from uuid import UUID

import pytest
from app.application.use_cases import (
    GenerateProceduralCards,
    GenerateProceduralCardsCommand,
)
from app.infrastructure.generators import ProceduralCardAttributeGenerator
from app.infrastructure.repositories import InMemoryCardRepository, InMemoryCardSearchIndex
from app.infrastructure.workers import (
    ProceduralCardGenerationWorker,
    ProceduralCardGenerationWorkerConfig,
)
from super_trunfo_shared import InMemoryDomainEventPublisher
from super_trunfo_shared.cards import CardAttributes


def test_procedural_generation_persists_indexes_and_publishes_card_created() -> None:
    owner_id = UUID("11111111-1111-4111-8111-111111111111")
    batch_id = UUID("22222222-2222-4222-8222-222222222204")
    repository = InMemoryCardRepository()
    search_index = InMemoryCardSearchIndex()
    event_publisher = InMemoryDomainEventPublisher(
        service_name="card-service",
        context="cards",
    )
    use_case = GenerateProceduralCards(
        repository,
        SequentialAttributeGenerator([valid_attributes(), alternate_attributes()]),
        search_index,
        event_publisher,
    )

    result = use_case.execute(
        GenerateProceduralCardsCommand(
            owner_id=owner_id,
            family="shop",
            quantity=2,
            generation_batch_id=batch_id,
        )
    )

    indexed_cards = search_index.find_by_owner(owner_id)
    published_events = event_publisher.published_events()

    assert result.generation_batch_id == batch_id
    assert len(result.cards) == 2
    assert result.attempts == 2
    assert len(indexed_cards) == 2
    assert indexed_cards[0].generation_batch_id == batch_id
    assert len(published_events) == 2
    assert published_events[0].name == "CardCreated"
    assert published_events[0].payload["schema_version"] == "1.0.0"
    assert published_events[0].payload["generation_batch_id"] == str(batch_id)
    assert published_events[0].payload["card_id"] == str(result.cards[0].id)
    assert published_events[0].payload["uniqueness_hash"] == result.cards[0].uniqueness_hash


def test_procedural_generation_rejects_non_positive_quantity() -> None:
    use_case = GenerateProceduralCards(
        InMemoryCardRepository(),
        SequentialAttributeGenerator([valid_attributes()]),
        InMemoryCardSearchIndex(),
        InMemoryDomainEventPublisher(service_name="card-service", context="cards"),
    )

    with pytest.raises(ValueError, match="quantity"):
        use_case.execute(
            GenerateProceduralCardsCommand(
                owner_id=UUID("11111111-1111-4111-8111-111111111111"),
                family="shop",
                quantity=0,
            )
        )


def test_worker_run_once_generates_configured_batch() -> None:
    owner_id = UUID("11111111-1111-4111-8111-111111111111")
    event_publisher = InMemoryDomainEventPublisher(
        service_name="card-service",
        context="cards",
    )
    worker = ProceduralCardGenerationWorker(
        GenerateProceduralCards(
            InMemoryCardRepository(),
            SequentialAttributeGenerator([valid_attributes(), alternate_attributes()]),
            InMemoryCardSearchIndex(),
            event_publisher,
        ),
        ProceduralCardGenerationWorkerConfig(
            owner_id=owner_id,
            family="shop",
            batch_size=2,
        ),
    )

    result = worker.run_once()

    assert len(result.cards) == 2
    assert len(event_publisher.published_events()) == 2


@pytest.mark.parametrize(
    ("roll", "expected_rarity"),
    [
        (0.49, 1),
        (0.50, 50),
        (0.80, 75),
        (0.95, 90),
    ],
)
def test_generator_uses_configured_rarity_distribution(
    roll: float,
    expected_rarity: int,
) -> None:
    generator = ProceduralCardAttributeGenerator(FixedRandomSource(roll))

    assert generator.generate_rarity() == expected_rarity


class SequentialAttributeGenerator:
    def __init__(self, attributes: list[CardAttributes]) -> None:
        self.attributes = attributes
        self.index = 0

    def generate(self) -> CardAttributes:
        generated = self.attributes[self.index]
        self.index += 1
        return generated


class FixedRandomSource:
    def __init__(self, roll: float) -> None:
        self.roll = roll

    def random(self) -> float:
        return self.roll

    def randint(self, start: int, _end: int) -> int:
        return start

    def choice(self, values: tuple[str, ...]) -> str:
        return values[0]


def valid_attributes() -> CardAttributes:
    return CardAttributes(
        name="Solar Titan",
        speed=70,
        strength=62,
        intelligence=58,
        resistance=64,
        rarity=80,
    )


def alternate_attributes() -> CardAttributes:
    return CardAttributes(
        name="Shadow Ranger",
        speed=72,
        strength=61,
        intelligence=59,
        resistance=63,
        rarity=81,
    )
