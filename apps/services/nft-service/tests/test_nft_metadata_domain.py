from datetime import UTC, datetime
from uuid import UUID

import pytest
from app.application.use_cases import (
    GenerateNftMetadata,
    GenerateNftMetadataCommand,
    command_from_card_created_payload,
)
from app.domain.entities import NftAttribute, NftMetadata, create_nft_metadata
from app.domain.exceptions import NftInvariantError
from app.infrastructure.repositories import InMemoryNftMetadataRepository
from super_trunfo_shared import InMemoryDomainEventPublisher


def test_metadata_uses_erc721_shape_with_mint_disabled() -> None:
    metadata = create_nft_metadata(
        card_id=UUID("22222222-2222-4222-8222-222222222205"),
        card_name="Solar Titan",
        family="solar",
        rarity=80,
        level=334,
        speed=70,
        strength=62,
        intelligence=58,
        resistance=64,
        generated_at=datetime(2026, 6, 2, tzinfo=UTC),
    )

    erc721_json = metadata.to_erc721_json()

    assert erc721_json["name"] == "Super Trunfo NFT - Solar Titan"
    assert erc721_json["description"]
    assert erc721_json["image"] == (
        "ipfs://super-trunfo-nft/cards/22222222-2222-4222-8222-222222222205.png"
    )
    assert erc721_json["attributes"] == [
        {"trait_type": "Family", "value": "solar"},
        {"trait_type": "Rarity", "value": 80},
        {"trait_type": "Level", "value": 334},
        {"trait_type": "Speed", "value": 70},
        {"trait_type": "Strength", "value": 62},
        {"trait_type": "Intelligence", "value": 58},
        {"trait_type": "Resistance", "value": 64},
    ]
    assert erc721_json["properties"]["mint_enabled"] is False


def test_metadata_rejects_insecure_image_uri() -> None:
    insecure_image_uri = "http" + "://assets.example/cards/solar-titan.png"

    with pytest.raises(NftInvariantError, match="secure or decentralized"):
        NftMetadata(
            card_id=UUID("22222222-2222-4222-8222-222222222205"),
            name="Super Trunfo NFT - Solar Titan",
            description="Offline ERC-721 metadata.",
            image=insecure_image_uri,
            attributes=(NftAttribute("Family", "solar"),),
            generated_at=datetime(2026, 6, 2, tzinfo=UTC),
        )


def test_metadata_accepts_secure_image_uri() -> None:
    metadata = NftMetadata(
        card_id=UUID("22222222-2222-4222-8222-222222222205"),
        name="Super Trunfo NFT - Solar Titan",
        description="Offline ERC-721 metadata.",
        image="https://assets.example/cards/solar-titan.png",
        attributes=(NftAttribute("Family", "solar"),),
        generated_at=datetime(2026, 6, 2, tzinfo=UTC),
    )

    assert metadata.image == "https://assets.example/cards/solar-titan.png"


def test_generate_metadata_persists_and_publishes_event() -> None:
    repository = InMemoryNftMetadataRepository()
    event_publisher = InMemoryDomainEventPublisher(service_name="nft-service", context="nft")
    use_case = GenerateNftMetadata(repository, event_publisher)

    metadata = use_case.execute(
        GenerateNftMetadataCommand(
            card_id=UUID("22222222-2222-4222-8222-222222222205"),
            card_name="Solar Titan",
            family="solar",
            rarity=80,
            level=334,
        )
    )

    events = event_publisher.published_events()

    assert repository.find_by_card_id(metadata.card_id) == metadata
    assert len(events) == 1
    assert events[0].name == "NftMetadataGenerated"
    assert events[0].payload["schema_version"] == "1.0.0"
    assert events[0].payload["card_id"] == str(metadata.card_id)
    assert events[0].payload["metadata_uri"] == metadata.metadata_uri
    assert events[0].payload["mint_enabled"] is False


def test_card_created_payload_can_prepare_metadata_command() -> None:
    command = command_from_card_created_payload(
        {
            "card_id": "22222222-2222-4222-8222-222222222205",
            "name": "Solar Titan",
            "family": "solar",
            "rarity": 80,
            "level": 334,
            "expires_at": "2027-07-07T00:00:00+00:00",
        }
    )

    assert command.card_id == UUID("22222222-2222-4222-8222-222222222205")
    assert command.card_name == "Solar Titan"
    assert command.family == "solar"
    assert command.rarity == 80
    assert command.level == 334
    assert command.expires_at == datetime(2027, 7, 7, tzinfo=UTC)
