from pymongo import MongoClient

from src.config.settings import Settings


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
            print('MongoDB connected')
        else:
            print('MongoDB already connected')

    def _connect(self):
        self._client = MongoClient(self.host, self.port)
        self._db = self._client[self.database_name]

    def server_info(self):
        return self._client.server_info()

    def set_collection(self, collection: str):
        self.collection_name = collection
        self._collection = self._db[self.collection_name]

    def get_data_from_collection(self) -> list[dict]:
        documents = self._collection.find()
        return list(documents)

    def save_dataframe(self, df):
        data = df.to_dict(orient='records')
        self._collection.insert_many(data)
        print('DataFrame saved in MongoDB.')

    def close_connection(self):
        if self._client:
            self._client.close()
            print('Connection closed successfully.')
