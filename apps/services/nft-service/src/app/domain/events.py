from super_trunfo_shared import DomainEvent

from .entities import NftMetadata

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
