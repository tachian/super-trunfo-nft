from datetime import UTC, datetime, timedelta
from uuid import UUID

import pytest
from app.application.use_cases import (
    AcceptTrade,
    AcceptTradeCommand,
    CancelTrade,
    CancelTradeCommand,
    CreateTrade,
    CreateTradeCommand,
)
from app.domain.entities import (
    MarketplaceListingStatus,
    TradeStatus,
    create_marketplace_listing,
    create_trade_from_listing,
)
from app.domain.exceptions import NftInvariantError
from app.infrastructure.repositories import (
    InMemoryMarketplaceListingRepository,
    InMemoryTradeRepository,
)
from super_trunfo_shared import InMemoryDomainEventPublisher

SELLER_ID = UUID("11111111-7040-4704-8704-000000000001")
BUYER_ID = UUID("22222222-7040-4704-8704-000000000001")
CARD_ID = UUID("33333333-7040-4704-8704-000000000001")


def active_listing():
    created_at = datetime.now(UTC)

    return create_marketplace_listing(
        seller_id=SELLER_ID,
        card_id=CARD_ID,
        token_id=704,
        price=7,
        expires_at=created_at + timedelta(days=7),
        created_at=created_at,
    )


def test_trade_is_created_from_active_marketplace_listing() -> None:
    listing = active_listing()
    trade = create_trade_from_listing(
        listing=listing,
        buyer_id=BUYER_ID,
        created_at=datetime.now(UTC),
    )

    assert trade.status == TradeStatus.CREATED
    assert trade.listing_id == listing.id
    assert trade.seller_id == SELLER_ID
    assert trade.buyer_id == BUYER_ID
    assert trade.card_id == CARD_ID
    assert trade.token_id == 704
    assert trade.price == 7


def test_trade_rejects_same_seller_and_buyer() -> None:
    with pytest.raises(NftInvariantError, match="different players"):
        create_trade_from_listing(listing=active_listing(), buyer_id=SELLER_ID)


def test_trade_rejects_inactive_marketplace_listing() -> None:
    listing = active_listing().cancel()

    with pytest.raises(NftInvariantError, match="active listing"):
        create_trade_from_listing(listing=listing, buyer_id=BUYER_ID)


def test_create_trade_persists_and_publishes_trade_created() -> None:
    listing_repository = InMemoryMarketplaceListingRepository()
    trade_repository = InMemoryTradeRepository()
    event_publisher = InMemoryDomainEventPublisher(service_name="nft-service", context="nft")
    listing = active_listing()
    listing_repository.save(listing)
    use_case = CreateTrade(listing_repository, trade_repository, event_publisher)

    result = use_case.execute(CreateTradeCommand(listing_id=listing.id, buyer_id=BUYER_ID))

    events = event_publisher.published_events()

    assert trade_repository.find_by_id(result.trade.id) == result.trade
    assert result.trade.status == TradeStatus.CREATED
    assert len(events) == 1
    assert events[0].name == "TradeCreated"
    assert events[0].payload["trade_id"] == str(result.trade.id)
    assert events[0].payload["status"] == TradeStatus.CREATED.value


def test_accept_trade_publishes_trade_accepted_and_nft_transferred() -> None:
    listing_repository = InMemoryMarketplaceListingRepository()
    trade_repository = InMemoryTradeRepository()
    event_publisher = InMemoryDomainEventPublisher(service_name="nft-service", context="nft")
    listing = active_listing()
    trade = create_trade_from_listing(listing=listing, buyer_id=BUYER_ID)
    listing_repository.save(listing)
    trade_repository.save(trade)
    use_case = AcceptTrade(listing_repository, trade_repository, event_publisher)

    result = use_case.execute(AcceptTradeCommand(trade_id=trade.id))

    events = event_publisher.published_events()
    saved_listing = listing_repository.find_by_id(listing.id)

    assert result.trade.status == TradeStatus.ACCEPTED
    assert trade_repository.find_by_id(trade.id) == result.trade
    assert saved_listing.status == MarketplaceListingStatus.SOLD
    assert [event.name for event in events] == ["TradeAccepted", "NFTTransferred"]
    assert events[1].payload["from_player_id"] == str(SELLER_ID)
    assert events[1].payload["to_player_id"] == str(BUYER_ID)
    assert events[1].payload["token_id"] == 704


def test_cancel_trade_publishes_trade_cancelled() -> None:
    trade_repository = InMemoryTradeRepository()
    event_publisher = InMemoryDomainEventPublisher(service_name="nft-service", context="nft")
    trade = create_trade_from_listing(listing=active_listing(), buyer_id=BUYER_ID)
    trade_repository.save(trade)
    use_case = CancelTrade(trade_repository, event_publisher)

    result = use_case.execute(
        CancelTradeCommand(
            trade_id=trade.id,
            reason="buyer withdrew offer",
        )
    )

    events = event_publisher.published_events()

    assert result.trade.status == TradeStatus.CANCELLED
    assert result.trade.cancellation_reason == "buyer withdrew offer"
    assert events[0].name == "TradeCancelled"
    assert events[0].payload["cancellation_reason"] == "buyer withdrew offer"
