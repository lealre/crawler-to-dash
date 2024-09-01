from pymongo import MongoClient, errors

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
        self._client = MongoClient(
            self.host, self.port, serverSelectionTimeoutMS=7000
        )
        self._db = self._client[self.database_name]
    
    def ping(self) -> bool:
        """Pings the MongoDB server to check if the connection is alive."""
        try:
            self._client.admin.command('ping')
            return True
        except errors.ServerSelectionTimeoutError:
            print("Server selection timed out. Unable to connect.")
            return False
        except errors.PyMongoError as e:
            print(f"An error occurred while connecting to MongoDB: {e}")
            return False

    def set_collection(self, collection: str):
        self._collection = self._db[collection]

    def get_data_from_collection(self) -> list[dict]:
        documents = self._collection.find()
        return list(documents)

    def save_data(self, collection: str, data: list[dict]):
        self.set_collection(collection=collection)

        if data:
            try:
                self._collection.insert_many(data)
                print(f'Json saved in MongoDB. Added {len(data)} recods.')
            except errors.BulkWriteError as e:
                error_details = e.details if hasattr(e, 'details') else str(e)
                error_message = (
                    f'An error occurred while inserting documents '
                    'into MongoDB:\n'
                    f'Error Code: {e.code}\n'
                    f'Error Message: {
                        e.details.get(
                            'writeErrors', 'No detailed message available'
                        )
                    }'
                    f'\nFull Error Details: {error_details}'
                )
                raise RuntimeError(error_message) from e
        else:
            print('There are no records to insert.')

    def close_connection(self):
        if self._client:
            self._client.close()
            print('Connection closed successfully.')
