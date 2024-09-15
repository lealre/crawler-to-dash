import pandas as pd

from src.core.mongodb import MongoConnection
from src.core.settings import settings

class Data():
    def __init__(self) -> None:
        self.df = self.get_data()

    @staticmethod
    def get_data() -> pd.DataFrame:

        data = MongoConnection().get_data_from_collection(
            collection=settings.COLLECTION_DASH
        )
            
        df = pd.DataFrame(data)

        return df[
            (df.transaction == 'SELL') &
            (df.areaInSquareMeters > 10) &
            (df.areaInSquareMeters < 500_000)
        ]
