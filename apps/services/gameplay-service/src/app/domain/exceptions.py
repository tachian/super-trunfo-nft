class GameplayInvariantError(ValueError):
    """Raised when gameplay aggregates violate domain invariants."""


class MatchNotFoundError(LookupError):
    """Raised when a match is not available in the repository."""
