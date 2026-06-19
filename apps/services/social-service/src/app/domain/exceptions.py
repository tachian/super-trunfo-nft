class SocialInvariantError(ValueError):
    """Raised when a social domain invariant is violated."""


class FriendInviteNotFoundError(LookupError):
    """Raised when a friend invite is not available."""
