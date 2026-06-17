class NftInvariantError(ValueError):
    """Raised when NFT metadata violates domain invariants."""


class NftMetadataNotFoundError(LookupError):
    """Raised when offline metadata is not available for a card."""


class MarketplaceListingNotFoundError(LookupError):
    """Raised when a marketplace listing is not available."""
