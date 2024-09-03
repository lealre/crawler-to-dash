import json
from abc import ABC, abstractmethod
from datetime import datetime

from src.core.mongodb import MongoConnection
from src.core.settings import Settings

settings = Settings()


class AbstractCrawler(ABC):
    def __init__(self, site_name: str):
        self.data: list[dict] = []
        self.site_name = site_name
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
            'AppleWebKit/537.36 (KHTML, like Gecko)'
            'Chrome/58.0.3029.110 Safari/537.3'
        }
        self.output_path = settings.LOCAL_BACKUP_PATH
        self.mongo = MongoConnection()

    @abstractmethod
    def crawl(self):
        pass

    def check_before_crawl(self):
        self.save_to_mongo = settings.SAVE_TO_MONGO
        self.local_storage = settings.LOCAL_STORAGE

        if self.save_to_mongo:
            if self.mongo.ping():
                print('Data will be stored in mongoDB')
            else:
                raise SystemExit('Its not possible to save data in MongoDB.')
        if self.local_storage:
            print('Data will be stored locally as Json file')

    def save_local_json(self) -> None:
        day_extracted = datetime.now().strftime('%d_%m_%Y')
        file_name = f'raw_{self.site_name}_{day_extracted}'
        path_to_save = f'{self.output_path}/{file_name}.json'

        try:
            with open(path_to_save, 'w', encoding='utf-8') as json_file:
                json.dump(self.data, json_file, indent=4)
            print(f"Json file saved in '{self.output_path}' as '{file_name}'")
        except Exception as e:
            print('Error exporting the file:', str(e))

    def save_data(self):
        collection_name = f'raw_{self.site_name}'
        try:
            self.mongo.save_data(data=self.data, collection=collection_name)
        except Exception:
            raise ('It was not possible to save the data in MongoDB')
