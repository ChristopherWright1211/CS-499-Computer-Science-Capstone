"""Custom exceptions for the Grazioso Salvare application."""


class AnimalShelterError(Exception):
    """Base exception for application-level errors."""


class ConfigurationError(AnimalShelterError):
    """Raised when required application configuration is missing or invalid."""


class ValidationError(AnimalShelterError):
    """Raised when input data does not meet application requirements."""


class RepositoryError(AnimalShelterError):
    """Raised when a database operation cannot be completed safely."""
