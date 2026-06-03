from typing import Protocol
from uuid import UUID

from .entities import NftMetadata


class NftMetadataRepository(Protocol):
    def save(self, metadata: NftMetadata) -> None:
        """Persist offline NFT metadata."""

    def find_by_card_id(self, card_id: UUID) -> NftMetadata | None:
        """Find offline NFT metadata by card id."""
