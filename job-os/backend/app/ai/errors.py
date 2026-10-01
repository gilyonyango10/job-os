class AIProviderError(Exception):
    """Raised when the configured AI provider cannot complete a request."""


class AIProviderNotConfigured(AIProviderError):
    """Raised when no AI provider is configured for extraction."""


class AIResponseInvalid(AIProviderError):
    """Raised when the provider returns data that cannot be used."""


class EmptyJobDescription(ValueError):
    """Raised when a job has no description to extract from."""
