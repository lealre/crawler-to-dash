from src.core.mongodb import MongoConnection


class Consolidate:
    def __init__(
        self,
        raw_collection='raw_imovirtual',
        consolidated_collection='consolidated_imovirtual',
    ) -> None:
        """
        Initializes the Consolidate class with MongoDB connections and loads
        data from the raw and consolidated collections.

        Parameters:
        ----------
        raw_collection : str, optional
            The name of the MongoDB collection containing raw data
            (default is 'raw_imovirtual').
        consolidated_collection : str, optional
            The name of the MongoDB collection containing consolidated data
            (default is 'consolidated_imovirtual').
        """

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
        """
        Main method to consolidate data by filtering unique ads, updating
        their availability, and inserting new ads into the consolidated
        collection.
        """

        self.filtered_data: list[dict] = (
            self.filter_unique_and_add_availability(self.raw_data)
        )

        self.update_availability()
        self.insert_new_ads()

    def update_availability(self) -> None:
        """
        Updates the availability status of ads in the consolidated collection.
        Compares the consolidated data with the filtered raw data to determine
        which ads' availability needs to be updated.
        """

        ids_to_update = self.ads_to_update_availability(
            consolidated_data=self.consolidated_data,
            filtered_data=self.filtered_data,
        )

        self.mongo.update_is_available(
            collection=self.consolidated_collection,
            unique_index='id',
            ids=ids_to_update,
        )

    def insert_new_ads(self) -> None:
        """
        Inserts new ads that are not present in the consolidated collection.
        Compares the consolidated data with filtered data and saves
        new entries into the collection.
        """

        new_ads = self.new_ads_to_insert(
            consolidated_data=self.consolidated_data,
            filtered_data=self.filtered_data,
        )

        self.mongo.save_data(
            collection=self.consolidated_collection, data=new_ads
        )

    @staticmethod
    def ads_to_update_availability(
        consolidated_data: list[dict], filtered_data: list[dict]
    ) -> list[str]:
        """
        Identifies ads that need their availability status updated.

        Parameters:
        ----------
        consolidated_data : list[dict]
            The list of ads from the consolidated collection.
        filtered_data : list[dict]
            The filtered list of ads from the raw data.

        Returns:
        -------
        list[str]
            A list of ad IDs whose availability status needs to be updated.
        """

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
    def new_ads_to_insert(
        consolidated_data: list[dict], filtered_data: list[dict]
    ) -> list[dict]:
        """
        Identifies new ads that need to be inserted into the consolidated
        collection.

        Parameters:
        ----------
        consolidated_data : list[dict]
            The list of ads from the consolidated collection.
        filtered_data : list[dict]
            The filtered list of ads from the raw data.

        Returns:
        -------
        list[dict]
            A list of new ads to be inserted into the consolidated collection.
        """
        consolidated_ids = [item.get('id') for item in consolidated_data]

        ads_to_insert: list = [
            item
            for item in filtered_data
            if item.get('id') not in consolidated_ids
        ]

        return ads_to_insert

    @staticmethod
    def filter_unique_and_add_availability(data: list[dict]) -> list[dict]:
        """
        Filters out duplicate ads based on their 'id' and adds an
        'is_available' key to each ad, marking it as available.

        Parameters:
        ----------
        data : list[dict]
            The raw data to be filtered for unique entries.

        Returns:
        -------
        list[dict]
            A filtered list containing only unique ads with the
            'is_available' flag set to True.
        """
        seen = set()
        data_filtered: list = []
        for item in data:
            id = item.get('id')
            item['is_available'] = True
            if id not in seen:
                seen.add(id)
                data_filtered.append(item)

        return data_filtered


if __name__ == '__main__':
    consolidate = Consolidate(raw_collection='raw_imovirtual')

    consolidate.consolidate()
