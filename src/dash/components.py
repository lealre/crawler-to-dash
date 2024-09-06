from dash import html, dcc
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from src.dash.data import get_data

df = get_data()

def card_component(title, data):
    component = dbc.Col(
                    dbc.Card(
                        dbc.CardBody([
                            html.H4(title),
                            html.H4(data)
                        ], style= {'color': 'white'}), 
                        color="dark", 
                        outline=True,
                        className = 'text-dark',
                        style={'textAlign': 'center', 'margin-bottom': '20px'}
                    ),
                )
    return component


def overall_component():
    color_scale = px.colors.sequential.Viridis 
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
    
    component = dbc.Row([
        html.H2('Overall Information', style={'padding-bottom': '20px'}),
        dcc.Graph(figure=fig)
    ])

    return component

def heatmap_component():

    pivot_df = df.pivot_table(
        index='location', 
        columns='roomsNumberNotation', 
        values='pricePerSquareMeter', 
        aggfunc='median'
    )

    pivot_df = pivot_df.apply(pd.to_numeric, errors='coerce')
    pivot_df = pivot_df.fillna(0)


    heatmap = go.Figure(data=go.Heatmap(
        z=pivot_df.values,
        x=pivot_df.columns,
        y=pivot_df.index,
        colorscale='Blugrn', 
        colorbar=dict(title='Price per Square Meter'),
        zmin=pivot_df.values.min(),
        zmax=pivot_df.values.max(),
        text = pivot_df.values,
        texttemplate="%{text:.2f}", 
        textfont=dict(size=12, color='black'),
    ))

    heatmap.update_layout(
        title='Heatmap of Price per Square Meter',
        xaxis_title='Location',
        yaxis_title='Rooms Number Notation'
    )

    component = dbc.Row([
        html.H2(
            'Price per m2 - Location x Rooms Number', 
            style={'padding-bottom': '20px'}
        ),
        dcc.Graph(figure=heatmap)
    ])

    return component