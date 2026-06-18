from threading import Lock
from uuid import UUID

from app.domain.entities import (
    MarketplaceListing,
    MarketplaceListingStatus,
    NftMetadata,
    Trade,
)


class InMemoryNftMetadataRepository:
    def __init__(self) -> None:
        self._metadata_by_card_id: dict[UUID, NftMetadata] = {}
        self._lock = Lock()

    def save(self, metadata: NftMetadata) -> None:
        with self._lock:
            self._metadata_by_card_id[metadata.card_id] = metadata

    def find_by_card_id(self, card_id: UUID) -> NftMetadata | None:
        return self._metadata_by_card_id.get(card_id)

    def clear(self) -> None:
        with self._lock:
            self._metadata_by_card_id.clear()


class InMemoryMarketplaceListingRepository:
    def __init__(self) -> None:
        self._listings_by_id: dict[UUID, MarketplaceListing] = {}
        self._lock = Lock()

    def save(self, listing: MarketplaceListing) -> None:
        with self._lock:
            self._listings_by_id[listing.id] = listing

    def find_by_id(self, listing_id: UUID) -> MarketplaceListing | None:
        return self._listings_by_id.get(listing_id)

    def list_active(self) -> tuple[MarketplaceListing, ...]:
        with self._lock:
            listings = []

            for listing in self._listings_by_id.values():
                resolved_listing = listing.expire()
                self._listings_by_id[resolved_listing.id] = resolved_listing

                if resolved_listing.status == MarketplaceListingStatus.ACTIVE:
                    listings.append(resolved_listing)

        return tuple(listings)

    def clear(self) -> None:
        with self._lock:
            self._listings_by_id.clear()


class InMemoryTradeRepository:
    def __init__(self) -> None:
        self._trades_by_id: dict[UUID, Trade] = {}
        self._lock = Lock()

    def save(self, trade: Trade) -> None:
        with self._lock:
            self._trades_by_id[trade.id] = trade

    def find_by_id(self, trade_id: UUID) -> Trade | None:
        return self._trades_by_id.get(trade_id)

    def clear(self) -> None:
        with self._lock:
            self._trades_by_id.clear()
