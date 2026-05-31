class IdentityError(Exception):
    """Base exception for identity domain errors."""


class PlayerAlreadyExistsError(IdentityError):
    """Raised when email or nickname is already registered."""


class InvalidCredentialsError(IdentityError):
    """Raised when authentication fails without exposing which field failed."""
