from pymongo import MongoClient
from bson.objectid import ObjectId


class AnimalShelter:
    """CRUD operations for Animal collection in MongoDB."""

    def __init__(self, username, password):
        self.client = MongoClient(
            f"mongodb://{username}:{password}@localhost:27017/AAC?authSource=admin"
        )
        self.database = self.client["aac"]
        self.collection = self.database["animals"]

    def create(self, data):
        if data is not None:
            result = self.collection.insert_one(data)
            return result.acknowledged
        else:
            raise Exception("Nothing to save because data parameter is empty")

    def read(self, query):
        if query is not None:
            data = self.collection.find(query)
            return list(data)
        else:
            raise Exception("Nothing to read because query parameter is empty")

    def update(self, query, new_values):
        if query is not None and new_values is not None:
            result = self.collection.update_many(query, {"$set": new_values})
            return result.modified_count
        else:
            raise Exception("Query or new values are empty")

    def delete(self, query):
        if query is not None:
            result = self.collection.delete_many(query)
            return result.deleted_count
        else:
            raise Exception("Nothing to delete because query parameter is empty")