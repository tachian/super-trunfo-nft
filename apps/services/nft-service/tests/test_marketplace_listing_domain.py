from datetime import UTC, datetime, timedelta
from uuid import UUID

import pytest
from super_trunfo_shared import InMemoryDomainEventPublisher

from app.application.use_cases import (
    CreateMarketplaceListing,
    CreateMarketplaceListingCommand,
    ListMarketplaceListings,
)
from app.domain.entities import (
    MarketplaceListingStatus,
    create_marketplace_listing,
)
from app.domain.exceptions import NftInvariantError
from app.infrastructure.repositories import InMemoryMarketplaceListingRepository


SELLER_ID = UUID("11111111-7030-4703-8703-000000000001")
CARD_ID = UUID("22222222-7030-4703-8703-000000000001")


def test_marketplace_listing_starts_active_with_history() -> None:
    created_at = datetime(2026, 6, 17, 10, 0, tzinfo=UTC)
    listing = create_marketplace_listing(
        seller_id=SELLER_ID,
        card_id=CARD_ID,
        token_id=703,
        price=5,
        expires_at=created_at + timedelta(days=7),
        created_at=created_at,
    )

    assert listing.status == MarketplaceListingStatus.ACTIVE
    assert listing.price == 5
    assert listing.expires_at == datetime(2026, 6, 24, 10, 0, tzinfo=UTC)
    assert listing.history[0].status == MarketplaceListingStatus.ACTIVE
    assert listing.history[0].reason == "listing created"


def test_marketplace_listing_rejects_invalid_price() -> None:
    created_at = datetime(2026, 6, 17, 10, 0, tzinfo=UTC)

    with pytest.raises(NftInvariantError, match="price must be positive"):
        create_marketplace_listing(
            seller_id=SELLER_ID,
            card_id=CARD_ID,
            token_id=703,
            price=0,
            expires_at=created_at + timedelta(days=7),
            created_at=created_at,
        )


def test_marketplace_listing_rejects_expiration_before_creation() -> None:
    created_at = datetime(2026, 6, 17, 10, 0, tzinfo=UTC)

    with pytest.raises(NftInvariantError, match="expiration must be after creation"):
        create_marketplace_listing(
            seller_id=SELLER_ID,
            card_id=CARD_ID,
            token_id=703,
            price=5,
            expires_at=created_at,
            created_at=created_at,
        )


def test_marketplace_listing_status_transitions_append_history() -> None:
    created_at = datetime(2026, 6, 17, 10, 0, tzinfo=UTC)
    listing = create_marketplace_listing(
        seller_id=SELLER_ID,
        card_id=CARD_ID,
        token_id=703,
        price=5,
        expires_at=created_at + timedelta(days=7),
        created_at=created_at,
    )

    cancelled = listing.cancel(cancelled_at=created_at + timedelta(hours=1))

    assert cancelled.status == MarketplaceListingStatus.CANCELLED
    assert len(cancelled.history) == 2
    assert cancelled.history[-1].reason == "seller cancelled listing"


def test_expired_marketplace_listing_is_removed_from_active_list() -> None:
    created_at = datetime.now(UTC) - timedelta(days=2)
    repository = InMemoryMarketplaceListingRepository()
    listing = create_marketplace_listing(
        seller_id=SELLER_ID,
        card_id=CARD_ID,
        token_id=703,
        price=5,
        expires_at=created_at + timedelta(hours=1),
        created_at=created_at,
    )
    repository.save(listing)

    assert repository.list_active() == ()
    assert repository.find_by_id(listing.id).status == MarketplaceListingStatus.EXPIRED


def test_create_marketplace_listing_persists_and_publishes_event() -> None:
    repository = InMemoryMarketplaceListingRepository()
    event_publisher = InMemoryDomainEventPublisher(service_name="nft-service", context="nft")
    use_case = CreateMarketplaceListing(repository, event_publisher)

    result = use_case.execute(
        CreateMarketplaceListingCommand(
            seller_id=SELLER_ID,
            card_id=CARD_ID,
            token_id=703,
            price=5,
            expires_at=datetime.now(UTC) + timedelta(days=7),
        )
    )

    events = event_publisher.published_events()

    assert repository.find_by_id(result.listing.id) == result.listing
    assert len(events) == 1
    assert events[0].name == "MarketplaceListingCreated"
    assert events[0].payload["listing_id"] == str(result.listing.id)
    assert events[0].payload["status"] == MarketplaceListingStatus.ACTIVE.value


def test_list_marketplace_listings_returns_active_listings() -> None:
    created_at = datetime(2026, 6, 17, 10, 0, tzinfo=UTC)
    repository = InMemoryMarketplaceListingRepository()
    use_case = ListMarketplaceListings(repository)
    active_listing = create_marketplace_listing(
        seller_id=SELLER_ID,
        card_id=CARD_ID,
        token_id=703,
        price=5,
        expires_at=datetime.now(UTC) + timedelta(days=7),
        created_at=created_at,
    )
    cancelled_listing = create_marketplace_listing(
        seller_id=SELLER_ID,
        card_id=UUID("22222222-7030-4703-8703-000000000002"),
        token_id=704,
        price=6,
        expires_at=datetime.now(UTC) + timedelta(days=7),
        created_at=created_at,
    ).cancel(cancelled_at=created_at + timedelta(hours=1))
    repository.save(active_listing)
    repository.save(cancelled_listing)

    result = use_case.execute()

    assert result.listings == (active_listing,)
