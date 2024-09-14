import json
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path

from src.core.mongodb import MongoConnection
from src.core.s3_client import S3Client
from src.core.settings import Settings

settings = Settings()


class AbstractCrawler(ABC):
    def __init__(self, site_name: str):
        '''
        Initializes an AbstractCrawler instance.

        Sets up the initial state for the crawler, including the data list,
        site name, headers for HTTP requests, output path for storing data,
        and file name for saving crawled data. The file name is generated
        using the site name and the current date.

        Args:
            site_name (str): The name of the site to crawl.
        '''

        self.data: list[dict] = []
        self.site_name = site_name
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
            'AppleWebKit/537.36 (KHTML, like Gecko)'
            'Chrome/58.0.3029.110 Safari/537.3'
        }
        self.output_path = settings.LOCAL_BACKUP_PATH

        day_extracted = datetime.now().strftime('%d_%m_%Y')
        self.file_name = f'raw_{self.site_name}_{day_extracted}'

    @abstractmethod
    def crawl(self):
        pass

    def check_before_crawl(self) -> None:
        '''
        Checks the configuration and connectivity of storage options before
        crawling.

        Verifies the availability of MongoDB, local storage, and AWS S3 based
        on the settings. Initializes the appropriate storage connections and
        ensures that the storage paths are valid. Raises a SystemExit
        exception if any storage configuration is invalid or if no storage
        options are enabled.

        Raises:
            SystemExit: If there are issues with storage configuration
            or connectivity.
        '''
        self.mongo_storage = settings.USE_STORAGE_MONGO
        self.local_storage = settings.USE_STORAGE_LOCAL
        self.aws_s3_storage = settings.USE_STORAGE_AWS_S3

        if self.mongo_storage:
            self.mongo = MongoConnection()
            if self.mongo.ping():
                print('Data will be stored in mongoDB')
            else:
                raise SystemExit('Its not possible to save data in MongoDB.')

        if self.local_storage:
            path = Path(self.output_path)
            if path.is_dir():
                print('Data will be stored locally as JSON file')
            else:
                raise SystemExit(
                    'It is not possible to save the data locally because '
                    f'"{self.output_path}" is not a directory.'
                )

        if self.aws_s3_storage:
            print('Data will be stored in the AWS S3 bucket.')
            self.s3_client = S3Client()

        if not any(
            [self.mongo_storage, self.local_storage, self.aws_s3_storage]
        ):
            raise SystemExit(
                'The crawled data will not be saved to any storage type'
                '(MongoDB, AWS S3, or Local). Please configure the storage'
                'settings in the .env file or in settings.py.'
            )

    def save_json_locally(self) -> None:
        '''
        Saves the JSON data to a local file.

        The file is saved in the specified directory with UTF-8 encoding.
        The filename follows the pattern 'raw_<site-name>_<day-extracted>'.

        Raises:
            Exception: If an error occurs during the file writing process.
        '''

        path_to_save = f'{self.output_path}/{self.file_name}.json'

        try:
            with open(path_to_save, 'w', encoding='utf-8') as json_file:
                json.dump(self.data, json_file, indent=4)
            print(
                f'Json file saved in "{self.output_path}"'
                f' as "{self.file_name}".'
            )
        except Exception as e:
            print('Error exporting the file:', str(e))

    def save_json_to_mongodb(self) -> None:
        '''
        Save the crawled data to MongoDB.

        The data is saved in a collection named with the site name
        and a 'raw_' prefix.


        Raises:
            Exception: If there is an error while saving the data to MongoDB.
        '''

        collection_name = f'raw_{self.site_name}'

        try:
            self.mongo.save_data(data=self.data, collection=collection_name)
        except Exception:
            raise ('It was not possible to save the data in MongoDB')

    def save_json_to_s3(self):
        '''
        Uploads the crawled data to the AWS S3 bucket specified in the .env
        file as a JSON file.

        Raises:
            Exception: Any exceptions related to connection issues with AWS S3.
        '''

        self.s3_client.upload_file(data=self.data, file_name=self.file_name)
