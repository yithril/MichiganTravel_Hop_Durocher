"""Custom exceptions for storage operations."""


class StorageError(Exception):
    """Base exception for storage operations."""
    pass


class ImageNotFoundError(StorageError):
    """Raised when an image is not found in storage."""
    pass


class StorageConfigurationError(StorageError):
    """Raised when storage configuration is invalid."""
    pass

