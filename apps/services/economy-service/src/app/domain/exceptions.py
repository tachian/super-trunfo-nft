class EconomyInvariantError(ValueError):
    """Raised when an economy domain rule is violated."""


class WalletNotFoundError(LookupError):
    """Raised when a wallet does not exist."""


class ShopOfferNotFoundError(LookupError):
    """Raised when a shop offer does not exist."""


class ShopOfferExpiredError(ValueError):
    """Raised when a shop offer is no longer active."""


class InsufficientCreditsError(ValueError):
    """Raised when a wallet cannot pay for a purchase."""
