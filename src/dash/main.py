import dash_bootstrap_components as dbc
from dash import Dash, html, dcc
import plotly.express as px 

from src.dash.data import get_data
from src.dash.components import get_card_component

df = get_data()

color_scale = px.colors.sequential.Viridis  # Use a continuous color scale like 'Viridis'
color_map = {f'T{i}': color_scale[i] for i in range(10)}
color_map['T9+'] = color_scale[-1]

fig = px.scatter(
    df,
    y = 'totalPrice', 
    x = 'areaInSquareMeters',
    color = 'roomsNumberNotation',
    color_discrete_map=color_map, 
    # size = 'totalPrice',
    log_x=True,
    log_y=True,
)


app = Dash(__name__, external_stylesheets=[dbc.themes. DARKLY])

app.layout = dbc.Container([
    html.H1('Lisbon Properties Dash', style={'textAlign':'center', 'padding-bottom': '20px'}),
    dbc.Row([
        get_card_component('Total Ads', df.shape[0]),
        get_card_component('Median Price', f'{df.totalPrice.median()} €'),
        get_card_component('Median Price / m2', f'{df.pricePerSquareMeter.median()} € / m2'),
    ]),
    dbc.Row([
        dcc.Graph(figure=fig)
    ])

],
style={'max-width': '90%'})


if __name__ == '__main__':
    app.run(debug=True)
