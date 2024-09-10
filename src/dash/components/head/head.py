import dash_bootstrap_components as dbc

from src.dash.components.utils.card import card_component
from src.dash.data import Data


class Head(Data):
    def __init__(self) -> None:
        super().__init__()
        self._component = self.get_component()

    def get_component(self):
        component = dbc.Row([
            dbc.Row([
                card_component('Total Listings', self.df.shape[0]),
                card_component(
                    'Median Price', f'{self.df.totalPrice.median()} €'
                ),
                card_component(
                    'Median Price per m²',
                    f'{self.df.pricePerSquareMeter.median()} € / m²',
                ),
            ],
    )
        ])

        return component

    @property
    def component(self):
        return self._component
