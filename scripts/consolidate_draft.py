from src.database.mongodb import MongoConnection

# with open(json_path, 'r', encoding='utf-8') as file:
#     data = json.load(file)


json_path = '_local/raw_imovirtual_test_01_09_2024.json'
raw_collection = 'raw_imovirtual_test_index'
collection_consolidated = 'consolidated_imovirtual'

mongo = MongoConnection()

consolidated_data = mongo.get_data_from_collection(
    collection=collection_consolidated
)
raw_data = mongo.get_data_from_collection(collection=raw_collection)

# Filter unique ids in raw
seen = set()
raw_filtered = []
for item in raw_data:
    id = item.get('id')
    item['is_available'] = True
    if id not in seen:
        seen.add(id)
        raw_filtered.append(item)


# Updated not availables
to_update_availability: list = []
for item in consolidated_data:
    id = item.get('id')
    if id not in raw_filtered and item.get('is_available', False):
        to_update_availability.append(id)


# Insert new ads
consolidated_ids = [item.get('id') for item in consolidated_data]

ads_to_add: list = []
for item in raw_filtered:
    id = item.get('id')
    if id not in consolidated_ids:
        ads_to_add.append(item)
