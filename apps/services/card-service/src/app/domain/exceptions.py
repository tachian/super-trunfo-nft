class CardInvariantError(ValueError):
    """Raised when a card aggregate violates a domain invariant."""


class DuplicateCardHashError(ValueError):
    """Raised when an identical card is already persisted."""


class DuplicateCardGenerationError(RuntimeError):
    """Raised when procedural generation cannot produce a unique card."""
