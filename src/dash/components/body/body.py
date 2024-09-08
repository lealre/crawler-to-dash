import dash_bootstrap_components as dbc
from dash import html

from src.dash.components.body import (
    scatter as ScatterComponent,
    treemap as TreemapComponent
)

from src.dash.data import Data


class Body(Data):
    def __init__(self) -> None:
        super().__init__()
        self.scatter_component = ScatterComponent.get_component(self.df)
        self._component = self.get_component()

    def get_component(self):
        component = dbc.Row([
            dbc.Col([html.P('Table here')], md=3),  # table(),
            dbc.Col(
                [
                    self.scatter_component,
                    # html.Br(),
                    # proportion_component(),
                    # html.Br(),
                    # heatmap_component(),
                ],
                md=9
            )
        ])

        return component

    @property
    def component(self):
        return self._component
