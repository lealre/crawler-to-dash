import json

json_path = '_local/raw_imovirtual_test_01_09_2024.json'

with open(json_path, 'r', encoding='utf-8') as file:
    data = json.load(file)

seen = set()
unique_id = []
for item in data:
    id = item.get('slug')
    if id not in seen:
        seen.add(id)
        unique_id.append(id)

print(len(data))
print(len(unique_id))
