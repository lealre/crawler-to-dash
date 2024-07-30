import numpy as np
import pandas as pd

from src.tools.mongodb import MongoConnection


class AbstractCleaner:
    def __init__(self, collection_in: str, collection_out: str) -> None:
        self.mongo_conn = MongoConnection()
        self.collection_in = collection_in
        self.collection_out = collection_out

    def get_collection_dataframe(self):
        self.mongo_conn.set_collection(collection=self.collection_in)
        data = self.mongo_conn.get_data_from_collection()
        self.df = pd.DataFrame(data)

    def normalize_and_reindex_dataframe(self):
        self.df = self.df.fillna(np.nan)
        self.df['is_available'] = True
        self.df = self.df.map(lambda x: x.strip() if isinstance(x, str) else x)

        desired_columns = [
            'title',
            'price_euro',
            'area_m2',
            'num_bedrooms',
            'property_status',
            'location_zone_0',
            'location_zone_1',
            'location_zone_2',
            'location_zone_3',
            'location_zone_4',
            'location_zone_5',
            'location_zone_6',
            'is_available',
            'site',
            'link_id',
            'link',
            'offer_type_search',
            'property_type_search',
            'location_search',
            'sub_location_search',
            'date_extracted',
        ]

        self.df = self.df.reindex(columns=desired_columns)

    def save_data(self, df: pd.DataFrame):
        try:
            self.mongo_conn.set_collection(collection=self.collection_out)
            self.mongo_conn.save_dataframe(df)
        except Exception:
            raise ('It was not possible to save the data in MongoDB')
