import dash_bootstrap_components as dbc
from dash import html


def card_component(title, data):
    component = dbc.Col(
        [dbc.Card(
            dbc.CardBody(
                [html.H4(title), html.H4(data)], style={'color': 'white'}
            ),
            color='#2A3439',
            style={'textAlign': 'center', 'margin-bottom': '20px', },
        )],
    )
    return component
