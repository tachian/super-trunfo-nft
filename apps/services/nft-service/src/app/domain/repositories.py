from typing import Protocol
from uuid import UUID

from .entities import MarketplaceListing, NftMetadata


class NftMetadataRepository(Protocol):
    def save(self, metadata: NftMetadata) -> None:
        """Persist offline NFT metadata."""

    def find_by_card_id(self, card_id: UUID) -> NftMetadata | None:
        """Find offline NFT metadata by card id."""


class MarketplaceListingRepository(Protocol):
    def save(self, listing: MarketplaceListing) -> None:
        """Persist a marketplace listing."""

    def find_by_id(self, listing_id: UUID) -> MarketplaceListing | None:
        """Find a marketplace listing by id."""

    def list_active(self) -> tuple[MarketplaceListing, ...]:
        """List active marketplace listings."""
