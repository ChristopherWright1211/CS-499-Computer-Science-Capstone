"""Tests for Milestone Four database-focused enhancements."""

import sys
import types
import unittest
from unittest.mock import MagicMock, Mock

# The course/Codio environment supplies pymongo. The local grading test below
# provides a tiny import stub so repository behavior can be unit-tested without
# requiring a live MongoDB installation.
try:
    import pymongo  # noqa: F401
except ModuleNotFoundError:
    pymongo_stub = types.ModuleType("pymongo")
    pymongo_stub.ASCENDING = 1
    pymongo_stub.DESCENDING = -1
    pymongo_stub.MongoClient = MagicMock
    errors_stub = types.ModuleType("pymongo.errors")
    class PyMongoError(Exception):
        pass
    errors_stub.PyMongoError = PyMongoError
    sys.modules["pymongo"] = pymongo_stub
    sys.modules["pymongo.errors"] = errors_stub

from config import MongoConfig
from exceptions import ValidationError
from repository import AnimalRepository
from service import AnimalService


class ServiceDatabaseEnhancementTests(unittest.TestCase):
    def setUp(self):
        self.repository = Mock()
        self.service = AnimalService(self.repository)

    def test_read_supports_projection_paging_and_sort(self):
        self.repository.read.return_value = [{"animal_id": "A1"}]
        result = self.service.read(
            {"animal_type": "Dog"},
            projection={"animal_id": 1, "breed": 1, "_id": 0},
            limit=25,
            skip=50,
            sort=[("animal_id", 1)],
        )
        self.assertEqual([{"animal_id": "A1"}], result)
        self.repository.read.assert_called_once_with(
            {"animal_type": "Dog"},
            projection={"animal_id": 1, "breed": 1, "_id": 0},
            limit=25,
            skip=50,
            sort=[("animal_id", 1)],
        )

    def test_read_rejects_excessive_limit(self):
        with self.assertRaises(ValidationError):
            self.service.read({}, limit=5001)

    def test_aggregate_limit_is_validated(self):
        with self.assertRaises(ValidationError):
            self.service.aggregate_breed_counts({}, limit=0)

    def test_database_summary_delegates_to_repository(self):
        self.repository.database_summary.return_value = {"total": 4}
        self.assertEqual({"total": 4}, self.service.database_summary({"animal_type": "Dog"}))


class RepositoryDatabaseEnhancementTests(unittest.TestCase):
    def make_repository(self):
        client = MagicMock()
        database = MagicMock()
        collection = MagicMock()
        client.__getitem__.return_value = database
        database.__getitem__.return_value = collection
        config = MongoConfig(username="u", password="p")
        repo = AnimalRepository(config, client=client)
        return repo, collection

    def test_ensure_indexes_creates_expected_indexes(self):
        repo, collection = self.make_repository()
        collection.create_index.side_effect = ["idx_animal_id", "idx_rescue_filter", "idx_location"]
        names = repo.ensure_indexes()
        self.assertEqual(["idx_animal_id", "idx_rescue_filter", "idx_location"], names)
        self.assertEqual(3, collection.create_index.call_count)

    def test_count_uses_count_documents(self):
        repo, collection = self.make_repository()
        collection.count_documents.return_value = 17
        self.assertEqual(17, repo.count({"animal_type": "Dog"}))
        collection.count_documents.assert_called_once_with({"animal_type": "Dog"})

    def test_breed_counts_use_aggregation_pipeline(self):
        repo, collection = self.make_repository()
        collection.aggregate.return_value = iter([{"breed": "Labrador Retriever Mix", "count": 5}])
        result = repo.aggregate_breed_counts({"animal_type": "Dog"}, limit=10)
        self.assertEqual(5, result[0]["count"])
        pipeline = collection.aggregate.call_args.args[0]
        self.assertEqual({"$match": {"animal_type": "Dog"}}, pipeline[0])
        self.assertEqual({"$limit": 10}, pipeline[4])


if __name__ == "__main__":
    unittest.main()
