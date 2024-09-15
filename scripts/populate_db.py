'''
Script to populate the dashboard collection in MongoDB using JSON data
from the data folder.
'''

import json

from src.core.mongodb import MongoConnection

collection_name = 'teste'
json_path = 'scripts/data/data.json'

mongo = MongoConnection()

with open(json_path, 'r', encoding='UTF-8') as file:
    data = json.load(file)

mongo.save_data(data=data, collection=collection_name, unique_index='id')
