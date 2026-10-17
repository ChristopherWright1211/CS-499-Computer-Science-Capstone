"""MongoDB repository for animal records."""

from __future__ import annotations

import logging
from typing import Any, Mapping

from pymongo import MongoClient
from pymongo.errors import PyMongoError

from config import MongoConfig
from exceptions import RepositoryError

logger = logging.getLogger(__name__)


class AnimalRepository:
    """Isolates MongoDB access from application and presentation logic."""

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

    def create(self, data: Mapping[str, Any]) -> bool:
        """Insert one animal record and return whether MongoDB acknowledged it."""
        try:
            result = self._collection.insert_one(dict(data))
            logger.info("Animal record created")
            return bool(result.acknowledged)
        except PyMongoError as exc:
            logger.exception("MongoDB create operation failed")
            raise RepositoryError("The animal record could not be created.") from exc

    def read(self, query: Mapping[str, Any]) -> list[dict[str, Any]]:
        """Return animal records matching the supplied query."""
        try:
            records = list(self._collection.find(dict(query)))
            logger.info("Animal records read: %s", len(records))
            return records
        except PyMongoError as exc:
            logger.exception("MongoDB read operation failed")
            raise RepositoryError("Animal records could not be retrieved.") from exc

    def update(
        self,
        query: Mapping[str, Any],
        new_values: Mapping[str, Any],
    ) -> int:
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
