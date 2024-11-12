import csv
import json
from src.core.mongodb import MongoConnection

DASH_COLLECTION = 'dash'

mongo_client = MongoConnection()

data = mongo_client.get_data_from_collection(collection=DASH_COLLECTION)

csv_filename = 'output.csv'
json_filename = 'output.json'



# Write data to CSV
fieldnames = data[0].keys()
with open(csv_filename, mode='w', newline='', encoding='utf-8') as file:
    writer = csv.DictWriter(file, fieldnames=fieldnames)
    writer.writeheader()  
    writer.writerows(data)


# Dump data to JSON
with open(json_filename, mode='w', encoding='utf-8') as file:
    json.dump(data, file, ensure_ascii=False, indent=4) 


