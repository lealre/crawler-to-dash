from src.cleaners.sapo_cleaner import SapoCleaner

# mongo_conn = MongoConnection()

# collection_name = 'raw_imovirtual'
# mongo_conn.set_collection(collection= collection_name)

# documents = mongo_conn.get_data_from_collection()

# data = list(documents)

# df = pd.DataFrame(data)

SapoCleaner().clean_and_stage()
