from uuid import UUID

import pytest
from app.application.use_cases import GenerateUniqueCard, GenerateUniqueCardCommand
from app.domain.entities import create_card
from app.domain.exceptions import DuplicateCardGenerationError, DuplicateCardHashError
from app.infrastructure.repositories import InMemoryCardRepository
from super_trunfo_shared.cards import CardAttributes


def test_repository_blocks_identical_cards_by_sha256_hash() -> None:
    repository = InMemoryCardRepository()
    attributes = valid_attributes()
    owner_id = UUID("11111111-1111-4111-8111-111111111111")

    repository.add(
        create_card(
            owner_id=owner_id,
            attributes=attributes,
            family="solar",
        )
    )

    with pytest.raises(DuplicateCardHashError, match="identical card"):
        repository.add(
            create_card(
                owner_id=owner_id,
                attributes=attributes,
                family="solar",
            )
        )


def test_generation_regenerates_attributes_when_hash_already_exists() -> None:
    duplicate_attributes = valid_attributes()
    unique_attributes = CardAttributes(
        name="Solar Sentinel",
        speed=71,
        strength=63,
        intelligence=59,
        resistance=65,
        rarity=81,
    )
    repository = InMemoryCardRepository()
    repository.add(
        create_card(
            owner_id=UUID("11111111-1111-4111-8111-111111111111"),
            attributes=duplicate_attributes,
            family="solar",
        )
    )
    generator = SequentialAttributeGenerator([duplicate_attributes, unique_attributes])
    use_case = GenerateUniqueCard(repository, generator)

    result = use_case.execute(
        GenerateUniqueCardCommand(
            owner_id=UUID("22222222-2222-4222-8222-222222222222"),
            family="solar",
        )
    )

    assert result.attempts == 2
    assert result.card.attributes == unique_attributes
    assert repository.exists_by_uniqueness_hash(result.card.uniqueness_hash)


def test_generation_fails_when_all_attempts_collide() -> None:
    attributes = valid_attributes()
    repository = InMemoryCardRepository()
    repository.add(
        create_card(
            owner_id=UUID("11111111-1111-4111-8111-111111111111"),
            attributes=attributes,
            family="solar",
        )
    )
    generator = SequentialAttributeGenerator([attributes, attributes])
    use_case = GenerateUniqueCard(repository, generator, max_attempts=2)

    with pytest.raises(DuplicateCardGenerationError, match="unique card"):
        use_case.execute(
            GenerateUniqueCardCommand(
                owner_id=UUID("22222222-2222-4222-8222-222222222222"),
                family="solar",
            )
        )


class SequentialAttributeGenerator:
    def __init__(self, attributes: list[CardAttributes]) -> None:
        self.attributes = attributes
        self.index = 0

    def generate(self) -> CardAttributes:
        generated = self.attributes[self.index]
        self.index += 1
        return generated


def valid_attributes() -> CardAttributes:
    return CardAttributes(
        name="Solar Titan",
        speed=70,
        strength=62,
        intelligence=58,
        resistance=64,
        rarity=80,
    )
