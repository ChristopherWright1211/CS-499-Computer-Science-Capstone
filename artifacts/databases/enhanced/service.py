"""Business logic and validation for Grazioso Salvare animal records."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any, Protocol

from exceptions import ValidationError

SortSpec = Sequence[tuple[str, int]]


class AnimalRepositoryProtocol(Protocol):
    def ensure_indexes(self) -> list[str]: ...
    def create(self, data: Mapping[str, Any]) -> bool: ...
    def read(self, query: Mapping[str, Any], *, projection=None, limit=0, skip=0, sort=None) -> list[dict[str, Any]]: ...
    def count(self, query: Mapping[str, Any]) -> int: ...
    def aggregate_breed_counts(self, query: Mapping[str, Any], *, limit: int = 10) -> list[dict[str, Any]]: ...
    def database_summary(self, query: Mapping[str, Any]) -> dict[str, Any]: ...
    def update(self, query: Mapping[str, Any], new_values: Mapping[str, Any]) -> int: ...
    def delete(self, query: Mapping[str, Any]) -> int: ...
    def close(self) -> None: ...


class AnimalService:
    """Validates input and applies rules before database access."""

    def __init__(self, repository: AnimalRepositoryProtocol, *, allow_mass_changes: bool = False) -> None:
        self._repository = repository
        self._allow_mass_changes = allow_mass_changes

    @staticmethod
    def _require_mapping(value: Mapping[str, Any] | None, name: str, *, allow_empty: bool) -> dict[str, Any]:
        if value is None:
            raise ValidationError(f"{name} cannot be empty.")
        if not isinstance(value, Mapping):
            raise ValidationError(f"{name} must be a dictionary-like object.")
        normalized = dict(value)
        if not allow_empty and not normalized:
            raise ValidationError(f"{name} must contain at least one field.")
        return normalized

    @staticmethod
    def _nonnegative_integer(value: int, name: str) -> int:
        if not isinstance(value, int) or value < 0:
            raise ValidationError(f"{name} must be a nonnegative whole number.")
        return value

    def ensure_indexes(self) -> list[str]:
        return self._repository.ensure_indexes()

    def create(self, data: Mapping[str, Any] | None) -> bool:
        return self._repository.create(self._require_mapping(data, "Animal data", allow_empty=False))

    def read(
        self,
        query: Mapping[str, Any] | None,
        *,
        projection: Mapping[str, int] | None = None,
        limit: int = 0,
        skip: int = 0,
        sort: SortSpec | None = None,
    ) -> list[dict[str, Any]]:
        normalized = self._require_mapping(query, "Query", allow_empty=True)
        limit = self._nonnegative_integer(limit, "Limit")
        skip = self._nonnegative_integer(skip, "Skip")
        if limit > 5000:
            raise ValidationError("Limit cannot exceed 5000 records per request.")
        normalized_projection = None
        if projection is not None:
            normalized_projection = self._require_mapping(projection, "Projection", allow_empty=False)
        if normalized_projection is None and limit == 0 and skip == 0 and sort is None:
            return self._repository.read(normalized)
        return self._repository.read(
            normalized,
            projection=normalized_projection,
            limit=limit,
            skip=skip,
            sort=sort,
        )

    def count(self, query: Mapping[str, Any] | None) -> int:
        return self._repository.count(self._require_mapping(query, "Query", allow_empty=True))

    def aggregate_breed_counts(self, query: Mapping[str, Any] | None, *, limit: int = 10) -> list[dict[str, Any]]:
        normalized = self._require_mapping(query, "Query", allow_empty=True)
        if not isinstance(limit, int) or not 1 <= limit <= 50:
            raise ValidationError("Aggregation limit must be between 1 and 50.")
        return self._repository.aggregate_breed_counts(normalized, limit=limit)

    def database_summary(self, query: Mapping[str, Any] | None) -> dict[str, Any]:
        return self._repository.database_summary(self._require_mapping(query, "Query", allow_empty=True))

    def update(self, query: Mapping[str, Any] | None, new_values: Mapping[str, Any] | None) -> int:
        normalized_query = self._require_mapping(query, "Query", allow_empty=self._allow_mass_changes)
        normalized_values = self._require_mapping(new_values, "New values", allow_empty=False)
        return self._repository.update(normalized_query, normalized_values)

    def delete(self, query: Mapping[str, Any] | None) -> int:
        normalized_query = self._require_mapping(query, "Query", allow_empty=self._allow_mass_changes)
        return self._repository.delete(normalized_query)

    def close(self) -> None:
        self._repository.close()
