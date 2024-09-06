import dash_bootstrap_components as dbc
from dash import Dash, html

from src.dash.components import (
    card_component,
    heatmap_component,
    overall_component,
    proportion_component,
)
from src.dash.data import get_data

df = get_data()

app = Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])

app.layout = dbc.Container(
    [
        html.H1(
            'Lisbon Properties Dash',
            style={'textAlign': 'center', 'padding-bottom': '20px'},
        ),
        dbc.Row([
            card_component('Total Ads', df.shape[0]),
            card_component('Median Price', f'{df.totalPrice.median()} €'),
            card_component(
                'Median Price / m2',
                f'{df.pricePerSquareMeter.median()} € / m2',
            ),
        ]),
        overall_component(),
        html.Br(),
        proportion_component(),
        html.Br(),
        heatmap_component(),
    ],
    style={'max-width': '90%'},
)


if __name__ == '__main__':
    app.run(debug=True)
