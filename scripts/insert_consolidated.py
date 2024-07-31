import pandas as pd

from src.database.mongodb_consolidated import MongoDBConsolidated


def get_dataframe(collection: str) -> pd.DataFrame:
    mongo_conn.set_collection(collection=collection)
    data = mongo_conn.get_data_from_collection()
    return pd.DataFrame(data)


if __name__ == '__main__':

    collection_stage = 'stage_sapo'
    collection_consolidated = 'consolidated_sapo'
    mongo_conn = MongoDBConsolidated(
        collection=collection_consolidated, id='link_id'
    )

    df_stage = get_dataframe(collection_stage)
    df_consolidated = get_dataframe(collection_consolidated)

    # insert values
    new_ads = df_stage[~df_stage['link_id'].isin(df_consolidated['link_id'])].copy()
    mongo_conn.insert_consolidated(df=new_ads)

    # update avaiables
    # values_to_update = df_consolidated.copy()
    # values_to_update['is_available'] = df_consolidated['link_id'].isin(df_stage['link_id'])

    # mongo_conn.update_available_records(
    #     df = df_consolidated,
    #     collection= collection_consolidated,
    #     id_field= 'link_id'
    # )
