import pandas as pd
from pymongo import MongoClient

from src.core.settings import Settings


class MongoConnection:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._instance._client = None
            cls._instance._db = None
            cls._instance._collection = None
        return cls._instance

    def __init__(self):
        if self._client is None:
            self.host = Settings().MONGO_HOST
            self.port = Settings().MONGO_PORT
            self.database_name = Settings().MONGO_DATABASE
            self._connect()

    def _connect(self):
        self._client = MongoClient(self.host, self.port)
        self._db = self._client[self.database_name]

    def server_info(self):
        return self._client.server_info()

    def set_collection(self, collection: str):
        self._collection = self._db[collection]

    def get_data_from_collection(self) -> list[dict]:
        documents = self._collection.find()
        return list(documents)

    def save_data(self, collection: str, data: list[dict]):
        self.set_collection(collection=collection)
        if data:
            self._collection.insert_many(data, ordered=False)
            print(f'DataFrame saved in MongoDB. Added {len(data)} recods.')
        else:
            print('There are no records to insert.')

    def close_connection(self):
        if self._client:
            self._client.close()
            print('Connection closed successfully.')
