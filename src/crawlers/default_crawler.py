from abc import ABC, abstractmethod
from datetime import datetime

import pandas as pd

from src.config.settings import Settings
from src.tools.mongodb import MongoConnection


class AbstractCrawler(ABC):
    def __init__(self, site_name: str):
        self.data: list = []
        self.list_dfs: list[pd.DataFrame] = []
        self.page: int = 1
        self.site_name = site_name
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
            'AppleWebKit/537.36 (KHTML, like Gecko)'
            'Chrome/58.0.3029.110 Safari/537.3'
        }
        self.output_path = 'src/cleaners/notebooks/data/raw/'
        self.mongo = MongoConnection()

    @abstractmethod
    def crawl(self):
        pass

    def check_before_crawl(self):
        self.save_to_mongo = Settings().SAVE_TO_MONGO
        self.local_storage = Settings().LOCAL_STORAGE

        if self.save_to_mongo:
            print('Data will be stored in mongoDB')
        if self.local_storage:
            print('Data will be stored locally as parquet')

    def export_parquet_file(self, df: pd.DataFrame) -> None:
        day_extracted = datetime.now().strftime('%Y-%m-%d')
        file_name = f'raw_{self.site_name}_{day_extracted}'
        path_to_save = f'{self.output_path}{file_name}.parquet'

        try:
            df.to_parquet(path=path_to_save, index=False)
            print(
                f"Parquet file saved in '{self.output_path}' as '{file_name}'"
            )
        except Exception as e:
            print('Error exporting the file:', str(e))

    def save_data(self, data: pd.DataFrame):
        collection_name = f'raw_{self.site_name}'
        try:
            self.mongo.set_collection(collection_name)
            self.mongo.save_dataframe(data)
        except Exception:
            raise ('It was not possible to save the data in MongoDB')

    @staticmethod
    def print_url(r, *args, **kwargs):
        print(r.url)
