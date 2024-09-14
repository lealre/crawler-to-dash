import json

from src.core.mongodb import MongoConnection
from src.core.settings import settings

file_path = '_local/data.json'
collection = settings.DASH_COLLECTION

mongo = MongoConnection()

data = mongo.get_data_from_collection(collection=collection)

with open(file_path, 'w', encoding='utf-8') as file:
    json.dump(data, file, indent=4)
