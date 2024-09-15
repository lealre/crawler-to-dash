import dash_bootstrap_components as dbc
from dash import html

from src.dash.components.body import heatmap as HeatmapComponent
from src.dash.components.body import scatter as ScatterComponent
from src.dash.components.body import table as TableComponent
from src.dash.components.body import treemap as TreemapComponent
from src.dash.components.app import df


class Body():
    def __init__(self) -> None:
        self.scatter_component = ScatterComponent.get_component()
        self.treemap_component = TreemapComponent.get_component()
        self.heatmap_component = HeatmapComponent.get_component()
        self.table_component = TableComponent.get_component()
        self._component = self.get_component()

    def get_component(self):
        component = dbc.Row([
            dbc.Col(
                [
                    self.table_component
                ],
                style={'margin': '10px 0px 0px 0px'},
                md=3
            ),
            dbc.Col(
                [
                    self.scatter_component,
                    html.Br(),
                    self.treemap_component,
                    html.Br(),
                    self.heatmap_component,
                ],
                md=9
            )
        ])

        return component

    @property
    def component(self):
        return self._component
