class NotificationInvariantError(ValueError):
    """Raised when a notification business rule is violated."""


class NotificationNotFoundError(LookupError):
    """Raised when a notification cannot be found."""


class UnsupportedNotificationEventError(ValueError):
    """Raised when an external event cannot produce a notification."""
