import dash_bootstrap_components as dbc
from dash import html

from src.dash.components.utils.card import card_component
from src.dash.data import Data


class Head(Data):
    def __init__(self) -> None:
        super().__init__()
        self._component = self.get_component()

    def get_component(self):
        component = dbc.Row([
            html.H1(
                'Lisbon Properties Dash',
                style={'textAlign': 'center', 'padding-bottom': '20px'},
            ),
            dbc.Row([
                card_component('Total Ads', self.df.shape[0]),
                card_component('Median Price', f'{self.df.totalPrice.median()} €'),
                card_component(
                    'Median Price / m2',
                    f'{self.df.pricePerSquareMeter.median()} € / m2',
                ),
            ])
        ])

        return component

    @property
    def component(self):
        return self._component
