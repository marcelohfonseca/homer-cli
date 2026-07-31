"""Homer exception hierarchy.

All Homer exceptions inherit from HomerError. Each integration layer
has its own sub-class so callers can catch errors at the right level
of granularity.
"""


class HomerError(Exception):
    """Base class for all Homer errors."""


class ConfigurationError(HomerError):
    """Raised when required configuration is missing or invalid."""


class JiraError(HomerError):
    """Raised when a Jira API operation fails."""


class ClockifyError(HomerError):
    """Raised when a Clockify API operation fails."""
