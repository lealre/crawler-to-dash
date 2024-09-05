import pandas as pd

def get_data() -> pd.DataFrame:
    file = '_local/data.json'

    df = pd.read_json(file, orient='records', encoding='utf-8')

    return df[df.transaction == 'SELL']