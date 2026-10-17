"""MongoDB repository for Grazioso Salvare animal records.

Milestone Four adds database-focused capabilities: indexes, projections,
pagination, sorting, document counts, and server-side aggregation reports.
"""

from __future__ import annotations

import logging
from collections.abc import Iterable, Mapping, Sequence
from typing import Any

from pymongo import ASCENDING, DESCENDING, MongoClient
from pymongo.errors import PyMongoError

from config import MongoConfig
from exceptions import RepositoryError

logger = logging.getLogger(__name__)

SortSpec = Sequence[tuple[str, int]]


class AnimalRepository:
    """Isolates MongoDB access from presentation and business logic."""

    def __init__(self, config: MongoConfig, client: MongoClient | None = None) -> None:
        self._config = config
        try:
            self._client = client or MongoClient(
                config.uri,
                serverSelectionTimeoutMS=config.server_selection_timeout_ms,
            )
            self._database = self._client[config.database]
            self._collection = self._database[config.collection]
        except PyMongoError as exc:
            logger.exception("Failed to initialize MongoDB repository")
            raise RepositoryError("Unable to initialize the animal database.") from exc

    def ping(self) -> bool:
        """Verify that MongoDB is reachable and authentication succeeds."""
        try:
            self._client.admin.command("ping")
            return True
        except PyMongoError as exc:
            logger.exception("MongoDB connection check failed")
            raise RepositoryError("Unable to connect to the animal database.") from exc

    def ensure_indexes(self) -> list[str]:
        """Create indexes used by common dashboard queries.

        The indexes are intentionally non-unique because the historical course
        dataset may contain repeated values. MongoDB creates an index only when
        an equivalent one is not already present.
        """
        try:
            names = [
                self._collection.create_index(
                    [("animal_id", ASCENDING)],
                    name="idx_animal_id",
                ),
                self._collection.create_index(
                    [
                        ("animal_type", ASCENDING),
                        ("breed", ASCENDING),
                        ("sex_upon_outcome", ASCENDING),
                        ("age_upon_outcome_in_weeks", ASCENDING),
                    ],
                    name="idx_rescue_filter",
                ),
                self._collection.create_index(
                    [("location_lat", ASCENDING), ("location_long", ASCENDING)],
                    name="idx_location",
                ),
            ]
            logger.info("Database indexes ready: %s", names)
            return names
        except PyMongoError as exc:
            logger.exception("MongoDB index creation failed")
            raise RepositoryError("Database indexes could not be created.") from exc

    def create(self, data: Mapping[str, Any]) -> bool:
        """Insert one animal record and return whether MongoDB acknowledged it."""
        try:
            result = self._collection.insert_one(dict(data))
            logger.info("Animal record created")
            return bool(result.acknowledged)
        except PyMongoError as exc:
            logger.exception("MongoDB create operation failed")
            raise RepositoryError("The animal record could not be created.") from exc

    def read(
        self,
        query: Mapping[str, Any],
        *,
        projection: Mapping[str, int] | None = None,
        limit: int = 0,
        skip: int = 0,
        sort: SortSpec | None = None,
    ) -> list[dict[str, Any]]:
        """Return records with optional projection, paging, and server-side sort."""
        try:
            cursor = self._collection.find(
                dict(query),
                dict(projection) if projection is not None else None,
            )
            if sort:
                cursor = cursor.sort(list(sort))
            if skip:
                cursor = cursor.skip(skip)
            if limit:
                cursor = cursor.limit(limit)
            records = list(cursor)
            logger.info("Animal records read: %s", len(records))
            return records
        except PyMongoError as exc:
            logger.exception("MongoDB read operation failed")
            raise RepositoryError("Animal records could not be retrieved.") from exc

    def count(self, query: Mapping[str, Any]) -> int:
        """Count matching documents without transferring them to the application."""
        try:
            return int(self._collection.count_documents(dict(query)))
        except PyMongoError as exc:
            logger.exception("MongoDB count operation failed")
            raise RepositoryError("Animal records could not be counted.") from exc

    def aggregate_breed_counts(
        self,
        query: Mapping[str, Any],
        *,
        limit: int = 10,
    ) -> list[dict[str, Any]]:
        """Return top breeds using a MongoDB aggregation pipeline.

        Aggregating in MongoDB avoids transferring every document to Python just
        to compute counts for the dashboard chart.
        """
        pipeline: list[dict[str, Any]] = [
            {"$match": dict(query)},
            {"$match": {"breed": {"$nin": [None, ""]}}},
            {"$group": {"_id": "$breed", "count": {"$sum": 1}}},
            {"$sort": {"count": -1, "_id": 1}},
            {"$limit": limit},
            {"$project": {"_id": 0, "breed": "$_id", "count": 1}},
        ]
        try:
            return list(self._collection.aggregate(pipeline))
        except PyMongoError as exc:
            logger.exception("MongoDB breed aggregation failed")
            raise RepositoryError("Breed summary could not be generated.") from exc

    def database_summary(self, query: Mapping[str, Any]) -> dict[str, Any]:
        """Return a compact server-side summary for the selected population."""
        pipeline: list[dict[str, Any]] = [
            {"$match": dict(query)},
            {
                "$facet": {
                    "total": [{"$count": "count"}],
                    "animal_types": [
                        {"$group": {"_id": "$animal_type", "count": {"$sum": 1}}},
                        {"$sort": {"count": -1}},
                    ],
                    "sex_outcomes": [
                        {"$group": {"_id": "$sex_upon_outcome", "count": {"$sum": 1}}},
                        {"$sort": {"count": -1}},
                    ],
                }
            },
        ]
        try:
            result = list(self._collection.aggregate(pipeline))
            if not result:
                return {"total": 0, "animal_types": [], "sex_outcomes": []}
            first = result[0]
            total_rows = first.get("total", [])
            return {
                "total": int(total_rows[0]["count"]) if total_rows else 0,
                "animal_types": first.get("animal_types", []),
                "sex_outcomes": first.get("sex_outcomes", []),
            }
        except PyMongoError as exc:
            logger.exception("MongoDB summary aggregation failed")
            raise RepositoryError("Database summary could not be generated.") from exc

    def update(self, query: Mapping[str, Any], new_values: Mapping[str, Any]) -> int:
        """Update matching animal records and return the modified count."""
        try:
            result = self._collection.update_many(dict(query), {"$set": dict(new_values)})
            logger.info("Animal records updated: %s", result.modified_count)
            return int(result.modified_count)
        except PyMongoError as exc:
            logger.exception("MongoDB update operation failed")
            raise RepositoryError("Animal records could not be updated.") from exc

    def delete(self, query: Mapping[str, Any]) -> int:
        """Delete matching animal records and return the deleted count."""
        try:
            result = self._collection.delete_many(dict(query))
            logger.info("Animal records deleted: %s", result.deleted_count)
            return int(result.deleted_count)
        except PyMongoError as exc:
            logger.exception("MongoDB delete operation failed")
            raise RepositoryError("Animal records could not be deleted.") from exc

    def close(self) -> None:
        """Close the MongoDB client connection."""
        self._client.close()
