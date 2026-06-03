from dataclasses import dataclass
from datetime import datetime
from typing import Protocol
from uuid import UUID

from super_trunfo_shared import DomainEvent

from app.domain.entities import NftMetadata, create_nft_metadata
from app.domain.events import nft_metadata_generated_event
from app.domain.exceptions import NftMetadataNotFoundError
from app.domain.repositories import NftMetadataRepository


class DomainEventPublisher(Protocol):
    def publish(self, event: DomainEvent) -> None:
        """Publish a domain event."""


@dataclass(frozen=True)
class GenerateNftMetadataCommand:
    card_id: UUID
    card_name: str
    family: str
    rarity: int
    level: int
    speed: int | None = None
    strength: int | None = None
    intelligence: int | None = None
    resistance: int | None = None
    expires_at: datetime | None = None


@dataclass(frozen=True)
class GetNftMetadataQuery:
    card_id: UUID


class GenerateNftMetadata:
    def __init__(
        self,
        repository: NftMetadataRepository,
        event_publisher: DomainEventPublisher,
    ) -> None:
        self.repository = repository
        self.event_publisher = event_publisher

    def execute(self, command: GenerateNftMetadataCommand) -> NftMetadata:
        metadata = create_nft_metadata(
            card_id=command.card_id,
            card_name=command.card_name,
            family=command.family,
            rarity=command.rarity,
            level=command.level,
            speed=command.speed,
            strength=command.strength,
            intelligence=command.intelligence,
            resistance=command.resistance,
            expires_at=command.expires_at,
        )

        self.repository.save(metadata)
        self.event_publisher.publish(nft_metadata_generated_event(metadata))

        return metadata


class GetNftMetadata:
    def __init__(self, repository: NftMetadataRepository) -> None:
        self.repository = repository

    def execute(self, query: GetNftMetadataQuery) -> NftMetadata:
        metadata = self.repository.find_by_card_id(query.card_id)

        if metadata is None:
            raise NftMetadataNotFoundError("NFT metadata was not generated for card")

        return metadata


def command_from_card_created_payload(
    payload: dict[str, object],
) -> GenerateNftMetadataCommand:
    expires_at_value = payload.get("expires_at")
    expires_at = (
        datetime.fromisoformat(str(expires_at_value)) if expires_at_value is not None else None
    )

    return GenerateNftMetadataCommand(
        card_id=UUID(str(payload["card_id"])),
        card_name=str(payload["name"]),
        family=str(payload["family"]),
        rarity=int(payload["rarity"]),
        level=int(payload["level"]),
        expires_at=expires_at,
    )
