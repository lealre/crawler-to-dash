import dash_bootstrap_components as dbc
import pandas as pd
import plotly.graph_objects as go
from dash import dcc, html


def get_component(df: pd.DataFrame):

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
            l=0,  # Left margin
            r=0,  # Right margin
            t=0,  # Top margin
            b=0   # Bottom margin
        ),
        yaxis=dict(
            tickmode='array',  # Use custom tick values and labels
            tickvals=list(range(len(pivot_df.index))),  # Set positions of ticks
            ticktext=[f'{label}  ' for label in pivot_df.index],  # Add padding to labels
            automargin=True   # Automatically adjust margins to fit labels
    )
    )

    component = dbc.Row(
        [
            html.H2(
                'Price per m2 - Location x Rooms Number',
                style={'padding-bottom': '20px'},
            ),
            dcc.Graph(figure=heatmap),
        ],
        style={
            'backgroundColor': '#2A3439',
            'color': '#ffffff',
            'padding': '20px',
            'border-radius': '20px'
        }
    )

    return component
