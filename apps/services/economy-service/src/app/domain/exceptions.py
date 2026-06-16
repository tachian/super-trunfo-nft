class EconomyInvariantError(ValueError):
    """Raised when an economy domain rule is violated."""


class WalletNotFoundError(LookupError):
    """Raised when a wallet does not exist."""

