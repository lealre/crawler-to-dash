import pandas as pd
from pymongo import errors

from src.database.mongodb import MongoConnection


class MongoDBConsolidated(MongoConnection):
    def __init__(self, collection: str, id: str):
        super().__init__()
        self.id = id
        self.collection = collection

    def set_consolidated_collection(self):
        self.collection_name = self.collection
        self._collection = self._db[self.collection_name]
        self._collection.create_index([(self.id, 1)], unique=True)

    def insert_consolidated(self, df: pd.DataFrame):
        self.set_consolidated_collection()
        try:
            self.save_dataframe(collection=self.collection, df=df)
        except errors.BulkWriteError:
            print('Trying to insert duplicated values')

    # def update_available_records(self, collection: str, id_field: str, df):
    #     self.set_collection(collection)
    #     data = df.to_dict(orient='records')
    #     for record in data:
    #         if record.get('is_available', False):
    #             filter_query = {id_field: record[id_field]}
    #             update_query = {'$set': record}
    #             result = self._collection.update_one(
    #                 filter_query, update_query
    #             )
    #             if result.modified_count > 0:
    #                 print(
    #                     f'Updated record with {id_field} = {record[id_field]}'
    #                 )
    #             else:
    #                 print(
    #                     'No updates made for record with '
    #                     f'{id_field} = {record[id_field]}'
    #                 )
