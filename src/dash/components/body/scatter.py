import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
from dash import dcc, html, Input, Output

from src.dash.components.app import app
from src.dash.data import Data


def get_component(df: pd.DataFrame):

    dropdown_option = list(df['estate'].unique())

    component = dbc.Row([
        html.H2('Overall Information', style={'padding-bottom': '10px'}),
            dbc.Row([
                dbc.Col([
                    dcc.Dropdown(
                        dropdown_option,
                        value = None,
                        id='estate-type',
                        placeholder='Select Type of Property',
                    ),
                ], md = 3),
                dbc.Col([
                    dcc.Checklist(
                        ['Log X Axis', 'Log Y Axis'],
                        inline=True
                    )
                ], md = 3),
            dcc.Graph(id = 'scatter-figure'),
            html.Div([
                html.P('Area Slider'),
                dcc.RangeSlider(
                    -5, 
                    6, 
                    marks={i: f'Label{i}' for i in range(-5, 7)},
                    value=[-3, 4]
                )
            ])
        ])
    ])

    return component

'''
Callbacks
'''

@app.callback(
    Output('scatter-figure', 'figure'),
    Input('estate-type', 'value')
)
def scatter_plot(estate_type):
    df = Data().get_data()

    color_scale = px.colors.sequential.Viridis
    color_map = {f'T{i}': color_scale[i] for i in range(10)}
    color_map['T9+'] = color_scale[-1]

    if estate_type:
        df = df[df['estate'] == estate_type]

    fig = px.scatter(
        df,
        y='totalPrice',
        x='areaInSquareMeters',
        color='roomsNumberNotation',
        color_discrete_map=color_map,
        size = 'totalPrice',
        log_x=True,
        log_y=True,
    )

    return fig