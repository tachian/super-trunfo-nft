class IdentityError(Exception):
    """Base exception for identity domain errors."""


class PlayerAlreadyExistsError(IdentityError):
    """Raised when email or nickname is already registered."""


class InvalidCredentialsError(IdentityError):
    """Raised when authentication fails without exposing which field failed."""


class InvalidAccessTokenError(IdentityError):
    """Raised when a bearer token cannot authenticate a player."""


class PlayerNotFoundError(IdentityError):
    """Raised when an authenticated subject does not map to a known player."""
