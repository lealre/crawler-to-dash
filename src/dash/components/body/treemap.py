import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
from dash import dcc, html

from src.dash.components.app import app
from src.dash.data import Data


def get_component(df:pd.DataFrame):
    proportion = (
        df.value_counts(['roomsNumberNotation', 'location'], normalize=True)
        .to_frame()
        .reset_index()
    )

    fig = px.treemap(
        proportion,
        path=['location', 'roomsNumberNotation'],
        values='proportion',
        branchvalues='total',
    )
    fig.update_traces(
        texttemplate=(
            '<b>%{label}</b><br>'
            '%{percentParent:.2%} of Location<br>'
            '%{percentRoot:.2%} of Overall'
        ),
        hovertemplate=(
            '<b>%{label}</b><br>'
            'Location Percentage: %{percentParent:.2%}<br>'
            'Overall Percentage: %{percentRoot:.2%}<extra></extra>'
        ),
        textfont=dict(size=14),
    )

    fig.update_layout(
        margin=dict(l=16, r=16, t=16, b=16),
        template='plotly_dark'
    )

    component = dbc.Row([
        html.H2(
            'Ads proportio per Location and Number of Rooms',
            style={'padding-bottom': '20px'},
        ),
        dcc.Graph(figure=fig),
    ])

    return component