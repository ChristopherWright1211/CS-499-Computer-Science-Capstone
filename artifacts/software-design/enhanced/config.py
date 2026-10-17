"""Configuration management for the Grazioso Salvare MongoDB connection."""

from dataclasses import dataclass
import os
from urllib.parse import quote_plus

from exceptions import ConfigurationError


@dataclass(frozen=True)
class MongoConfig:
    """MongoDB settings used by the data-access layer."""

    username: str
    password: str
    host: str = "localhost"
    port: int = 27017
    database: str = "aac"
    collection: str = "animals"
    auth_source: str = "admin"
    server_selection_timeout_ms: int = 5000

    @property
    def uri(self) -> str:
        """Build a MongoDB URI without storing credentials in source code."""
        username = quote_plus(self.username)
        password = quote_plus(self.password)
        return (
            f"mongodb://{username}:{password}@{self.host}:{self.port}/"
            f"{self.database}?authSource={self.auth_source}"
        )

    @classmethod
    def from_env(cls) -> "MongoConfig":
        """Load database settings from environment variables."""
        username = os.getenv("AAC_USERNAME")
        password = os.getenv("AAC_PASSWORD")

        if not username or not password:
            raise ConfigurationError(
                "Database credentials are missing. Set AAC_USERNAME and AAC_PASSWORD."
            )

        try:
            port = int(os.getenv("AAC_PORT", "27017"))
            timeout = int(os.getenv("AAC_TIMEOUT_MS", "5000"))
        except ValueError as exc:
            raise ConfigurationError(
                "AAC_PORT and AAC_TIMEOUT_MS must contain whole numbers."
            ) from exc

        return cls(
            username=username,
            password=password,
            host=os.getenv("AAC_HOST", "localhost"),
            port=port,
            database=os.getenv("AAC_DATABASE", "aac"),
            collection=os.getenv("AAC_COLLECTION", "animals"),
            auth_source=os.getenv("AAC_AUTH_SOURCE", "admin"),
            server_selection_timeout_ms=timeout,
        )

    @classmethod
    def from_credentials(cls, username: str, password: str) -> "MongoConfig":
        """Create configuration from credentials supplied by existing client code."""
        if not username or not password:
            raise ConfigurationError("A database username and password are required.")
        return cls(username=username, password=password)
