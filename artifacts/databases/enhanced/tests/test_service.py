"""Unit tests for the AnimalService business layer."""

import unittest
from unittest.mock import Mock

from exceptions import ValidationError
from service import AnimalService


class AnimalServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.repository = Mock()
        self.service = AnimalService(self.repository)

    def test_create_valid_record(self) -> None:
        self.repository.create.return_value = True
        record = {"animal_id": "TEST001", "animal_type": "Dog"}

        result = self.service.create(record)

        self.assertTrue(result)
        self.repository.create.assert_called_once_with(record)

    def test_create_rejects_empty_record(self) -> None:
        with self.assertRaises(ValidationError):
            self.service.create({})

    def test_read_allows_empty_query(self) -> None:
        self.repository.read.return_value = [{"animal_id": "TEST001"}]

        result = self.service.read({})

        self.assertEqual(1, len(result))
        self.repository.read.assert_called_once_with({})

    def test_update_rejects_empty_query_by_default(self) -> None:
        with self.assertRaises(ValidationError):
            self.service.update({}, {"name": "Updated"})

    def test_delete_rejects_empty_query_by_default(self) -> None:
        with self.assertRaises(ValidationError):
            self.service.delete({})

    def test_update_valid_record(self) -> None:
        self.repository.update.return_value = 1

        count = self.service.update(
            {"animal_id": "TEST001"},
            {"name": "Scout"},
        )

        self.assertEqual(1, count)
        self.repository.update.assert_called_once_with(
            {"animal_id": "TEST001"},
            {"name": "Scout"},
        )

    def test_mass_change_can_be_enabled_explicitly(self) -> None:
        repository = Mock()
        repository.delete.return_value = 3
        service = AnimalService(repository, allow_mass_changes=True)

        count = service.delete({})

        self.assertEqual(3, count)
        repository.delete.assert_called_once_with({})


if __name__ == "__main__":
    unittest.main()
