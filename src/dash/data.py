import pandas as pd

from src.core.mongodb import MongoConnection
from src.core.settings import settings

MIN_AREA = 10
MAX_AREA = 500_000


class Data:
    def __init__(self) -> None:
        self.df = self.get_data()

    @staticmethod
    def get_data() -> pd.DataFrame:
        data = MongoConnection().get_data_from_collection(
            collection=settings.COLLECTION_DASH
        )

        df = pd.DataFrame(data)

        return df[
            (df.transaction == 'SELL')
            & (df.areaInSquareMeters > MIN_AREA)
            & (df.areaInSquareMeters < MAX_AREA)
        ]
