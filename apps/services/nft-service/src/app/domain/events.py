from super_trunfo_shared import DomainEvent

from .entities import MarketplaceListing, NftMetadata, Trade

NFT_EVENT_SCHEMA_VERSION = "1.0.0"


def nft_metadata_generated_event(metadata: NftMetadata) -> DomainEvent:
    return DomainEvent(
        name="NftMetadataGenerated",
        aggregate_id=str(metadata.card_id),
        payload={
            "schema_version": NFT_EVENT_SCHEMA_VERSION,
            "card_id": str(metadata.card_id),
            "metadata_uri": metadata.metadata_uri,
            "image": metadata.image,
            "mint_enabled": metadata.mint_enabled,
            "generated_at": metadata.generated_at.isoformat(),
        },
    )


def marketplace_listing_created_event(listing: MarketplaceListing) -> DomainEvent:
    return DomainEvent(
        name="MarketplaceListingCreated",
        aggregate_id=str(listing.id),
        payload={
            "schema_version": NFT_EVENT_SCHEMA_VERSION,
            "listing_id": str(listing.id),
            "seller_id": str(listing.seller_id),
            "card_id": str(listing.card_id),
            "token_id": listing.token_id,
            "price": listing.price,
            "status": listing.status.value,
            "expires_at": listing.expires_at.isoformat(),
            "created_at": listing.created_at.isoformat(),
        },
    )


def trade_created_event(trade: Trade) -> DomainEvent:
    return DomainEvent(
        name="TradeCreated",
        aggregate_id=str(trade.id),
        payload=trade_payload(trade),
    )


def trade_accepted_event(trade: Trade) -> DomainEvent:
    return DomainEvent(
        name="TradeAccepted",
        aggregate_id=str(trade.id),
        payload=trade_payload(trade),
    )


def trade_cancelled_event(trade: Trade) -> DomainEvent:
    payload = trade_payload(trade)
    payload["cancellation_reason"] = trade.cancellation_reason

    return DomainEvent(
        name="TradeCancelled",
        aggregate_id=str(trade.id),
        payload=payload,
    )


def nft_transferred_event(trade: Trade) -> DomainEvent:
    return DomainEvent(
        name="NFTTransferred",
        aggregate_id=str(trade.card_id),
        payload={
            "schema_version": NFT_EVENT_SCHEMA_VERSION,
            "trade_id": str(trade.id),
            "listing_id": str(trade.listing_id),
            "card_id": str(trade.card_id),
            "token_id": trade.token_id,
            "from_player_id": str(trade.seller_id),
            "to_player_id": str(trade.buyer_id),
            "transferred_at": (
                trade.accepted_at.isoformat() if trade.accepted_at is not None else None
            ),
        },
    )


def trade_payload(trade: Trade) -> dict[str, object]:
    return {
        "schema_version": NFT_EVENT_SCHEMA_VERSION,
        "trade_id": str(trade.id),
        "listing_id": str(trade.listing_id),
        "seller_id": str(trade.seller_id),
        "buyer_id": str(trade.buyer_id),
        "card_id": str(trade.card_id),
        "token_id": trade.token_id,
        "price": trade.price,
        "status": trade.status.value,
        "created_at": trade.created_at.isoformat(),
        "accepted_at": trade.accepted_at.isoformat() if trade.accepted_at is not None else None,
        "cancelled_at": (
            trade.cancelled_at.isoformat() if trade.cancelled_at is not None else None
        ),
    }
