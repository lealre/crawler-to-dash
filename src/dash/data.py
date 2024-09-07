import pandas as pd


class Data():
    def __init__(self) -> None:
        self.df = self.get_data()
        
    @staticmethod
    def get_data() -> pd.DataFrame:
        file = '_local/data.json'

        df = pd.read_json(file, orient='records', encoding='utf-8')

        return df[
            (df.transaction == 'SELL') &
            (df.areaInSquareMeters > 10) & 
            (df.areaInSquareMeters < 500_000)
        ]
