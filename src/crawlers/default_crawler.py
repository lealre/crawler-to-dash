from abc import ABC, abstractmethod
from datetime import datetime

import pandas as pd


class AbstractCrawler(ABC):
    def __init__(self, site_name):
        self.data = []
        self.list_dfs = []
        self.page = 1
        self.site_name = site_name
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
            'AppleWebKit/537.36 (KHTML, like Gecko)'
            'Chrome/58.0.3029.110 Safari/537.3'
        }
        self.output_path = 'src/cleaners/notebooks/data/raw/'

    @abstractmethod
    def crawl(self):
        pass

    def export_parquet_file(self) -> None:
        day_extracted = datetime.now().strftime('%Y-%m-%d')
        file_name = f'raw_{self.site_name}_{day_extracted}'
        path_to_save = f'{self.output_path}{file_name}.parquet'

        df = pd.concat(self.list_dfs, ignore_index=True, axis=0)

        try:
            df.to_parquet(path=path_to_save, index=False)
            print(f"Parquet file saved in '{self.output_path}' as '{file_name}'")
        except Exception as e:
            print('Error exporting the file:', str(e))

    @staticmethod
    def print_url(r, *args, **kwargs):
        print(r.url)
