from src.database.mongodb import MongoConnection


class Consolidate:
    def __init__(
        self,
        raw_collection='raw_imovirtual',
        consolidated_collection='consolidated_imovirtual',
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
        self.consolidated_data = self.mongo.get_data_from_collection(
            collection=self.consolidated_collection
        )

    def consolidate(self) -> None:
        self.filtered_data: list[dict] = (
            self.filter_unique_and_add_availability(self.raw_data)
        )

    @staticmethod
    def update_availability(
        consolidated_data: list[dict], filtered_data: list[dict]
    ) -> list[str]:
        filtered_ids = [item.get('id') for item in filtered_data]

        ids_to_update: list[str] = [
            item.get('id')
            for item in consolidated_data
            if (
                item.get('id') not in filtered_ids
                and item.get('is_available', False)
            )
        ]

        return ids_to_update

    @staticmethod
    def insert_new_ads(
        consolidated_data: list[dict], filtered_data: list[dict]
    ) -> list[dict]:
        consolidated_ids = [item.get('id') for item in consolidated_data]

        ads_to_insert: list = [
            item
            for item in filtered_data
            if item.get('id') not in consolidated_ids
        ]

        return ads_to_insert

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
