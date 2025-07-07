"""Custom exception classes for the web search agent system.

This module defines the exception hierarchy used throughout the system
to provide meaningful error handling and debugging information.
"""


class SearchAgentError(Exception):
    """Base exception class for all search agent errors."""
    pass


class ScrapingError(SearchAgentError):
    """Raised when web scraping operations fail."""
    pass


class NoResultsError(SearchAgentError):
    """Raised when a search operation returns no results."""
    pass


class ConfigurationError(SearchAgentError):
    """Raised when there are configuration-related issues."""
    pass


class APIError(SearchAgentError):
    """Raised when API calls fail."""
    pass


class TimeoutError(SearchAgentError):
    """Raised when operations timeout."""
    pass


class SearchException(SearchAgentError):
    """Raised when search operations fail."""
    pass