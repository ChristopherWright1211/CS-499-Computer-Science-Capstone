"""Business logic and validation for Grazioso Salvare animal records."""

from __future__ import annotations

import logging
from collections.abc import Mapping
from typing import Any, Protocol

from exceptions import ValidationError

logger = logging.getLogger(__name__)


class AnimalRepositoryProtocol(Protocol):
    """Interface required by AnimalService, which also makes testing easier."""

    def create(self, data: Mapping[str, Any]) -> bool: ...
    def read(self, query: Mapping[str, Any]) -> list[dict[str, Any]]: ...
    def update(self, query: Mapping[str, Any], new_values: Mapping[str, Any]) -> int: ...
    def delete(self, query: Mapping[str, Any]) -> int: ...
    def close(self) -> None: ...


class AnimalService:
    """Validates input and applies application rules before database access."""

    def __init__(
        self,
        repository: AnimalRepositoryProtocol,
        *,
        allow_mass_changes: bool = False,
    ) -> None:
        self._repository = repository
        self._allow_mass_changes = allow_mass_changes

    @staticmethod
    def _require_mapping(
        value: Mapping[str, Any] | None,
        name: str,
        *,
        allow_empty: bool,
    ) -> dict[str, Any]:
        if value is None:
            raise ValidationError(f"{name} cannot be empty.")
        if not isinstance(value, Mapping):
            raise ValidationError(f"{name} must be a dictionary-like object.")

        normalized = dict(value)
        if not allow_empty and not normalized:
            raise ValidationError(f"{name} must contain at least one field.")
        return normalized

    def create(self, data: Mapping[str, Any] | None) -> bool:
        """Validate and create one animal record."""
        normalized = self._require_mapping(data, "Animal data", allow_empty=False)
        return self._repository.create(normalized)

    def read(self, query: Mapping[str, Any] | None) -> list[dict[str, Any]]:
        """Validate and read matching records. An empty query intentionally means all."""
        normalized = self._require_mapping(query, "Query", allow_empty=True)
        return self._repository.read(normalized)

    def update(
        self,
        query: Mapping[str, Any] | None,
        new_values: Mapping[str, Any] | None,
    ) -> int:
        """Validate and update matching records."""
        normalized_query = self._require_mapping(
            query,
            "Query",
            allow_empty=self._allow_mass_changes,
        )
        normalized_values = self._require_mapping(
            new_values,
            "New values",
            allow_empty=False,
        )
        return self._repository.update(normalized_query, normalized_values)

    def delete(self, query: Mapping[str, Any] | None) -> int:
        """Validate and delete matching records."""
        normalized_query = self._require_mapping(
            query,
            "Query",
            allow_empty=self._allow_mass_changes,
        )
        return self._repository.delete(normalized_query)

    def close(self) -> None:
        """Release repository resources."""
        self._repository.close()
