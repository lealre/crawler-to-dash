import pandas as pd

from src.tools.mongodb import MongoConnection


class AbstractCleaner():
    def __init__(self, collection: str) -> None:
        self.mongo_conn = MongoConnection()
        self.mongo_conn.set_collection(collection=collection)

    def get_collection_dataframe(self):
        data = self.mongo_conn.get_data_from_collection()
        self.df = pd.DataFrame(data)
        return self.df
    
    def reindex_dataframe(self):
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
            'site',
            'link_id',
            'link', 
            'offer_type_search', 
            'property_type_search',
            'location_search',
            'sub_location_search',
            'date_extracted'
        ]

        self.df = self.df.reindex(columns=desired_columns)
