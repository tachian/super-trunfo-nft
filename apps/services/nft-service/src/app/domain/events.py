from super_trunfo_shared import DomainEvent

from .entities import MarketplaceListing, NftMetadata

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
