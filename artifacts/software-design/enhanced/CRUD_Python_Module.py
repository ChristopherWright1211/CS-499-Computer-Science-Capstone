"""Compatibility facade for the enhanced Grazioso Salvare application.

The public AnimalShelter class keeps the simple CRUD interface used by the original
CS 340 dashboard while delegating configuration, validation, business logic, and
MongoDB access to separate components.
"""

from __future__ import annotations

import logging
from collections.abc import Mapping
from typing import Any

from config import MongoConfig
from repository import AnimalRepository
from service import AnimalRepositoryProtocol, AnimalService

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s - %(message)s",
)
logger = logging.getLogger(__name__)


class AnimalShelter:
    """Facade that preserves the original create/read/update/delete interface."""

    def __init__(
        self,
        username: str | None = None,
        password: str | None = None,
        *,
        repository: AnimalRepositoryProtocol | None = None,
        allow_mass_changes: bool = False,
    ) -> None:
        if repository is not None:
            selected_repository = repository
        else:
            if username is None and password is None:
                config = MongoConfig.from_env()
            else:
                config = MongoConfig.from_credentials(username or "", password or "")
            selected_repository = AnimalRepository(config)

        self._service = AnimalService(
            selected_repository,
            allow_mass_changes=allow_mass_changes,
        )

    @classmethod
    def from_env(cls, *, allow_mass_changes: bool = False) -> "AnimalShelter":
        """Create the application using environment-based configuration."""
        return cls(allow_mass_changes=allow_mass_changes)

    def create(self, data: Mapping[str, Any] | None) -> bool:
        return self._service.create(data)

    def read(self, query: Mapping[str, Any] | None) -> list[dict[str, Any]]:
        return self._service.read(query)

    def update(
        self,
        query: Mapping[str, Any] | None,
        new_values: Mapping[str, Any] | None,
    ) -> int:
        return self._service.update(query, new_values)

    def delete(self, query: Mapping[str, Any] | None) -> int:
        return self._service.delete(query)

    def close(self) -> None:
        self._service.close()

    def __enter__(self) -> "AnimalShelter":
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.close()
