from pymongo import MongoClient, errors

from src.core.settings import settings


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
            self.host = settings.MONGO_HOST
            self.port = settings.MONGO_PORT
            self.database_name = settings.MONGO_DATABASE
            self._connect()

    def _connect(self) -> None:
        self._client = MongoClient(
            self.host,
            self.port,
            serverSelectionTimeoutMS=settings.MONGO_TIMEOUT,
        )
        self._db = self._client[self.database_name]

    def ping(self) -> bool:
        """Pings the MongoDB server to check if the connection is alive."""
        try:
            self._client.admin.command('ping')
            return True
        except errors.ServerSelectionTimeoutError:
            print('Server selection timed out. Unable to connect to MongoDB.')
            return False
        except errors.PyMongoError as e:
            print(f'An error occurred while connecting to MongoDB: {e}')
            return False

    def set_collection(self, collection: str, unique_index: str = '') -> None:
        self._collection = self._db[collection]

        if unique_index:
            collection_indexes = self._collection.index_information()
            indexes = [
                index_info['key'][0][0]
                for _, index_info in collection_indexes.items()
            ]

            if unique_index in indexes:
                print(
                    f'"{unique_index}" is already a unique index from '
                    f'"{collection}" collection'
                )
            else:
                self._collection.create_index([(unique_index, 1)], unique=True)
                print(
                    f'Unique index "{unique_index}" created for '
                    f'"{collection}" collection'
                )

    def save_data(
        self, collection: str, data: list[dict], unique_index: str = ''
    ) -> None:
        self.set_collection(collection=collection, unique_index=unique_index)

        if data:
            try:
                self._collection.insert_many(data)
                print(
                    'Data saved in MongoDB. '
                    f'Added {len(data)} records to {collection}'
                )
            except errors.BulkWriteError as e:
                print('It was not possible to save data in MongoDB.')
                raise SystemExit(
                    f'ERROR: {e.details['writeErrors'][0]['errmsg']}'
                )
        else:
            print('There are no records to insert.')

    def get_data_from_collection(
        self,
        collection: str,
        filter: dict | None = None,
        fields: list | None = None,
    ) -> list[dict]:
        self.set_collection(collection=collection)

        projection = {field: 1 for field in fields} if fields else None

        if not projection:
            projection = {'_id': 0}

        documents = self._collection.find(filter=filter, projection=projection)
        return list(documents)

    def update_is_available(
        self, collection: str, unique_index: str, ids: list[int]
    ) -> None:
        """Update 'is_available' to False for the given list of ids."""

        self.set_collection(collection=collection, unique_index=unique_index)
        try:
            result = self._collection.update_many(
                {'id': {'$in': ids}},
                {'$set': {'is_available': False}},
            )
            print(f'Matched {result.matched_count} documents.')
            print(f'Modified {result.modified_count} documents.')
        except errors.PyMongoError as e:
            print(f'An error occurred: {e}')

    def close_connection(self) -> None:
        if self._client:
            self._client.close()
            print('Connection closed successfully.')
