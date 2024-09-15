from pymongo import MongoClient, errors

from src.core.settings import settings


class MongoConnection:
    _instance = None

    def __new__(cls, *args, **kwargs):
        """
        Creates or returns the singleton instance of MongoConnection.

        Ensures that only one instance of MongoConnection exists throughout
        the application.
        """

        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._instance._client = None
            cls._instance._db = None
            cls._instance._collection = None
        return cls._instance

    def __init__(self):
        """
        Initializes the MongoConnection instance.

        Connects to the MongoDB server using configuration settings.
        This method will be called only once due to the singleton pattern.
        """

        if self._client is None:
            self.host = settings.MONGO_HOST
            self.port = settings.MONGO_PORT
            self.database_name = settings.MONGO_DATABASE
            self._connect()

    def _connect(self) -> None:
        """
        Establishes a connection to the MongoDB server.

        Initializes the MongoClient and selects the database as specified
        in the configuration settings.
        """
        self._client = MongoClient(
            self.host,
            self.port,
            serverSelectionTimeoutMS=settings.MONGO_TIMEOUT,
        )
        self._db = self._client[self.database_name]

    def ping(self) -> bool:
        """
        Pings the MongoDB server to check if the connection is alive.

        Returns:
            bool: True if the connection is successful, False otherwise.
        """

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
        """
        Sets the collection to interact with and optionally creates
        a unique index.

        Args:
            collection (str): The name of the collection to use.
            unique_index (str): The field to be indexed uniquely (if any).
        """

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
        """
        Saves a list of documents to the specified collection.

        Args:
            collection (str): The name of the collection where data will
            be saved.
            data (list[dict]): The list of documents to be inserted.
            unique_index (str): Optional; The unique index field to be used.

        Raises:
            SystemExit: If an error occurs during data insertion.
        """

        self.set_collection(collection=collection, unique_index=unique_index)

        if data:
            try:
                self._collection.insert_many(data)
                print(
                    'Data saved in MongoDB. '
                    f'Added {len(data)} records to "{collection}" collection.'
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
        """
        Retrieves data from the specified collection.

        Args:
            collection (str): The name of the collection to query.
            filter (dict | None): Optional; The filter criteria for the query.
            fields (list | None): Optional; The list of fields to include in
            the results.

        Returns:
            list[dict]: A list of documents retrieved from the collection.
        """

        self.set_collection(collection=collection)

        projection = {field: 1 for field in fields} if fields else None

        if not projection:
            projection = {'_id': 0}

        documents = self._collection.find(filter=filter, projection=projection)
        return list(documents)

    def update_is_available(
        self, collection: str, unique_index: str, ids: list[int]
    ) -> None:
        """
        Updates the 'is_available' field to False for the given list of ids.

        This method is used to update the availability status of ads in the
        consolidation collection based on the raw data that has been crawled.

        Args:
            collection (str): The name of the collection to update.
            unique_index (str): The unique index field to use.
            ids (list[int]): The list of ids to be updated.
        """

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
        """
        Closes the connection to the MongoDB server.

        Ensures that the connection is properly closed and
        resources are released.
        """

        if self._client:
            self._client.close()
            print('Connection closed successfully.')
