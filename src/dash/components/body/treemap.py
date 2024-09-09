import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
from dash import Input, Output, dcc, html

from src.dash.components.app import app
from src.dash.data import Data


def get_component(df: pd.DataFrame):

    dropdown_options = list(df['estate'].unique())

    component = dbc.Row(
        [
            html.H2(
                'Ads proportion per Location and Number of Rooms',
                style={'padding-bottom': '20px'},
            ),
            dbc.Row([
                dbc.Col(
                    [
                        dcc.Dropdown(
                            dropdown_options,
                            value=None,
                            id='estate-type-treemap',
                            placeholder='Select Type of Property',
                        ),
                    ],
                    md=3
                ),
                dcc.Graph(id='treemap-figure'),
            ])
        ],
        style={
            'backgroundColor': '#2A3439',
            'color': '#ffffff',
            'padding': '20px',
            'border-radius': '20px'
        }
    )

    return component


@app.callback(
    Output('treemap-figure', 'figure'),
    Input('estate-type-treemap', 'value'),
)
def treemap_plot(estate_type):

    df = Data().get_data()

    if estate_type:
        df = df[df['estate'] == estate_type]

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
        margin=dict(l=0, r=0, t=20, b=0),
        paper_bgcolor='rgba(0, 0, 0, 0)',
        # template='plotly_dark'
    )

    return fig
