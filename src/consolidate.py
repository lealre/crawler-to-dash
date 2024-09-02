from src.database.mongodb import MongoConnection

class ConsolidateImovirtual():
    def __init__(
            self, 
            raw_collection = 'raw_imovirtual', 
            consolidated_collection = 'consolidated_imovirtual'
    ) -> None:
        self.mongo = MongoConnection()
        self.raw_collection = raw_collection
        self.consolidated_collection = consolidated_collection
        self.raw_filtered: list[dict] = []
        self.to_update_availability: list[str] = []
        self.ads_to_insert: list[dict] = []

        self.raw_data = self.mongo.get_data_from_collection(
            collection=self.raw_collection
        )
        self.consolidate_data = self.mongo.get_data_from_collection(
            collection=self.consolidated_collection
        )
    
    def consolidate(self) -> None:
        self.data_filtered: list[dict] = self.filter_unique_and_add_availability(
            self.raw_data
        )

        self.update_availability()
    
    def update_availability(self):
        ids_to_update: list[str] =  [
            item.get('id') 
            for item in self.consolidate_data 
            if (
                id not in self.data_filtered
                and item.get('is_available', False)
            )
        ]

        ... # Update ids in MongoDB
        
    def insert_new_ads(self):
        consolidated_ids = [item.get('id') for item in self.consolidate_data]

        ads_to_add: list = [
            item 
            for item in self.data_filtered 
            if item.get('id') not in consolidated_ids
        ]

        ... # Insert items in MongoDB

    @staticmethod
    def filter_unique_and_add_availability(data: list[dict]) -> list[dict]:
        seen = set()
        data_filtered: list = []
        for item in data:
            id = item.get('id')
            item['is_available'] = True
            if id not in seen:
                seen.add(id)
                data_filtered.append(item)
        
        return data_filtered
        
