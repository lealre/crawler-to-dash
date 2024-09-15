import dash_bootstrap_components as dbc
import pandas as pd
import plotly.graph_objects as go
from dash import dcc, html

from src.dash.components.app import df


def get_component():

    pivot_df = df.pivot_table(
        index='location',
        columns='roomsNumberNotation',
        values='pricePerSquareMeter',
        aggfunc='median',
    )

    pivot_df = pivot_df.apply(pd.to_numeric, errors='coerce')
    pivot_df = pivot_df.fillna(0)

    heatmap = go.Figure(
        data=go.Heatmap(
            z=pivot_df.values,
            x=pivot_df.columns,
            y=pivot_df.index,
            colorscale='Blugrn',
            showscale=False,
            colorbar=dict(title='Price per Square Meter'),
            zmin=pivot_df.values.min(),
            zmax=pivot_df.values.max(),
            text=pivot_df.values,
            texttemplate='%{text:.2f}',
            textfont=dict(size=12, color='black'),
        )
    )

    heatmap.update_layout(
        title=None,
        showlegend=False,
        xaxis_title=None,
        yaxis_title=None,
        paper_bgcolor='rgba(0, 0, 0, 0)',
        font=dict(color='white'),
        margin=dict(
            l=0,
            r=0,
            t=0,
            b=0
        ),
        yaxis=dict(
            tickmode='array',
            tickvals=list(range(len(pivot_df.index))),
            ticktext=[f'{label}  ' for label in pivot_df.index],
            automargin=True
    )
    )

    component = dbc.Row(
        [
            html.H3(
                'Median Price per m² Based on Location and Number of Rooms',
                style={'padding-bottom': '20px'},
            ),
            dcc.Graph(figure=heatmap),
        ],
        style={
            'backgroundColor': '#2A3439',
            'color': '#ffffff',
            'padding': '20px',
            'border-radius': '20px',
            'margin': '10px 20px 10px 10px'
        }
    )

    return component
