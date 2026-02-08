class BotError(Exception):
    """Base exception for bot domain errors."""


class ConfigurationError(BotError):
    """Raised when required configuration is missing or invalid."""


class PermissionError(BotError):
    """Raised when a user lacks permissions for an action."""


class RateLimitError(BotError):
    """Raised when a user or channel exceeds rate limits."""


class ExternalServiceError(BotError):
    """Raised when an external service fails."""
