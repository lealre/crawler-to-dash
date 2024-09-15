import dash_bootstrap_components as dbc

from src.dash.components.utils.card import card_component
from src.dash.components.app import df


class Head():
    def __init__(self) -> None:
        self._component = self.get_component()

    @staticmethod
    def get_component():
        component = dbc.Row([
            dbc.Row([
                card_component('Total Listings', df.shape[0]),
                card_component(
                    'Median Price', f'{df.totalPrice.median()} €'
                ),
                card_component(
                    'Median Price per m²',
                    f'{df.pricePerSquareMeter.median()} € / m²',
                ),
            ],
    )
        ])

        return component

    @property
    def component(self):
        return self._component
