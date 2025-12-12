"""
Core exceptions for the Taxini application.

This module contains custom exceptions used throughout the application.
"""

class NotFoundException(Exception):
    """Exception raised when a requested resource is not found."""
    pass


class UnauthorizedException(Exception):
    """Exception raised when a user attempts an unauthorized action."""
    pass


class ValidationException(Exception):
    """Exception raised when validation fails."""
    pass


class ConflictException(Exception):
    """Exception raised when there's a conflict with existing data."""
    pass
