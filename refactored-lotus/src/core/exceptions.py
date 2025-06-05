"""
Custom exceptions for the Lotus application.

This module defines application-specific exceptions that provide
clear error messages and structured handling of error conditions.
"""

class LotusError(Exception):
    """Base exception class for all Lotus application exceptions."""
    pass

class ConfigError(LotusError):
    """Base exception for configuration-related errors."""
    pass

class FileError(LotusError):
    """Base exception for file-related errors."""
    pass

class ValidationError(LotusError):
    """Base exception for validation-related errors."""
    pass

# Configuration errors
class MissingConfigurationError(ConfigError):
    """Raised when a required configuration value is missing."""
    pass

class InvalidConfigurationError(ConfigError):
    """Raised when a configuration value is invalid."""
    pass

class WorkAreaNotFoundError(ConfigError):
    """Raised when the work area root directory is not specified or not found."""
    pass

class FubNotFoundError(ConfigError):
    """Raised when the FUB is not specified or not found."""
    pass

# File errors
class FileNotFoundError(FileError):
    """Raised when a required file is not found."""
    pass

class FileAccessError(FileError):
    """Raised when a file cannot be accessed due to permissions or other issues."""
    pass

class FileFormatError(FileError):
    """Raised when a file has an invalid format."""
    pass

# Validation errors
class LineValidationError(ValidationError):
    """Raised when a line fails validation."""
    pass

class DocumentValidationError(ValidationError):
    """Raised when a document fails validation."""
    pass