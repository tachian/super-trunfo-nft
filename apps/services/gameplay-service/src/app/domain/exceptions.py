class GameplayInvariantError(ValueError):
    """Raised when gameplay aggregates violate domain invariants."""


class MatchNotFoundError(LookupError):
    """Raised when a match is not available in the repository."""


class MatchPlayValidationError(ValueError):
    """Raised when a round play request is rejected by authoritative rules."""
