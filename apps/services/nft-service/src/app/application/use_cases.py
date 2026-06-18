from dataclasses import dataclass
from datetime import datetime
from typing import Protocol
from uuid import UUID

from super_trunfo_shared import DomainEvent

from app.domain.entities import (
    MarketplaceListing,
    NftMetadata,
    Trade,
    create_marketplace_listing,
    create_nft_metadata,
    create_trade_from_listing,
)
from app.domain.events import (
    marketplace_listing_created_event,
    nft_metadata_generated_event,
    nft_transferred_event,
    trade_accepted_event,
    trade_cancelled_event,
    trade_created_event,
)
from app.domain.exceptions import (
    MarketplaceListingNotFoundError,
    NftMetadataNotFoundError,
    TradeNotFoundError,
)
from app.domain.repositories import (
    MarketplaceListingRepository,
    NftMetadataRepository,
    TradeRepository,
)


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


@dataclass(frozen=True)
class CreateMarketplaceListingCommand:
    seller_id: UUID
    card_id: UUID
    token_id: int
    price: int
    expires_at: datetime


@dataclass(frozen=True)
class CreateMarketplaceListingResult:
    listing: MarketplaceListing
    events: tuple[DomainEvent, ...]


@dataclass(frozen=True)
class ListMarketplaceListingsResult:
    listings: tuple[MarketplaceListing, ...]


@dataclass(frozen=True)
class CreateTradeCommand:
    listing_id: UUID
    buyer_id: UUID


@dataclass(frozen=True)
class AcceptTradeCommand:
    trade_id: UUID


@dataclass(frozen=True)
class CancelTradeCommand:
    trade_id: UUID
    reason: str = "trade cancelled"


@dataclass(frozen=True)
class TradeResult:
    trade: Trade
    events: tuple[DomainEvent, ...]


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


class CreateMarketplaceListing:
    def __init__(
        self,
        repository: MarketplaceListingRepository,
        event_publisher: DomainEventPublisher,
    ) -> None:
        self.repository = repository
        self.event_publisher = event_publisher

    def execute(
        self,
        command: CreateMarketplaceListingCommand,
    ) -> CreateMarketplaceListingResult:
        listing = create_marketplace_listing(
            seller_id=command.seller_id,
            card_id=command.card_id,
            token_id=command.token_id,
            price=command.price,
            expires_at=command.expires_at,
        )
        self.repository.save(listing)

        event = marketplace_listing_created_event(listing)
        self.event_publisher.publish(event)

        return CreateMarketplaceListingResult(listing=listing, events=(event,))


class ListMarketplaceListings:
    def __init__(self, repository: MarketplaceListingRepository) -> None:
        self.repository = repository

    def execute(self) -> ListMarketplaceListingsResult:
        return ListMarketplaceListingsResult(listings=self.repository.list_active())


class CreateTrade:
    def __init__(
        self,
        listing_repository: MarketplaceListingRepository,
        trade_repository: TradeRepository,
        event_publisher: DomainEventPublisher,
    ) -> None:
        self.listing_repository = listing_repository
        self.trade_repository = trade_repository
        self.event_publisher = event_publisher

    def execute(self, command: CreateTradeCommand) -> TradeResult:
        listing = self.listing_repository.find_by_id(command.listing_id)

        if listing is None:
            raise MarketplaceListingNotFoundError("marketplace listing was not found")

        trade = create_trade_from_listing(listing=listing, buyer_id=command.buyer_id)
        self.trade_repository.save(trade)

        event = trade_created_event(trade)
        self.event_publisher.publish(event)

        return TradeResult(trade=trade, events=(event,))


class AcceptTrade:
    def __init__(
        self,
        listing_repository: MarketplaceListingRepository,
        trade_repository: TradeRepository,
        event_publisher: DomainEventPublisher,
    ) -> None:
        self.listing_repository = listing_repository
        self.trade_repository = trade_repository
        self.event_publisher = event_publisher

    def execute(self, command: AcceptTradeCommand) -> TradeResult:
        trade = self.trade_repository.find_by_id(command.trade_id)

        if trade is None:
            raise TradeNotFoundError("marketplace trade was not found")

        accepted_trade = trade.accept()
        listing = self.listing_repository.find_by_id(accepted_trade.listing_id)

        if listing is None:
            raise MarketplaceListingNotFoundError("marketplace listing was not found")

        self.listing_repository.save(listing.mark_sold())
        self.trade_repository.save(accepted_trade)

        events = (
            trade_accepted_event(accepted_trade),
            nft_transferred_event(accepted_trade),
        )

        for event in events:
            self.event_publisher.publish(event)

        return TradeResult(trade=accepted_trade, events=events)


class CancelTrade:
    def __init__(
        self,
        trade_repository: TradeRepository,
        event_publisher: DomainEventPublisher,
    ) -> None:
        self.trade_repository = trade_repository
        self.event_publisher = event_publisher

    def execute(self, command: CancelTradeCommand) -> TradeResult:
        trade = self.trade_repository.find_by_id(command.trade_id)

        if trade is None:
            raise TradeNotFoundError("marketplace trade was not found")

        cancelled_trade = trade.cancel(reason=command.reason)
        self.trade_repository.save(cancelled_trade)

        event = trade_cancelled_event(cancelled_trade)
        self.event_publisher.publish(event)

        return TradeResult(trade=cancelled_trade, events=(event,))


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
