import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
from dash import Input, Output, dcc, html

from src.dash.components.app import app
from src.dash.data import Data

AREA_MARKS_LABELS = {
    1: 'Min',
    2: '30',
    3: '50',
    4: '100',
    5: '150',
    6: '500',
    7: '1000',
    8: '10K',
    9: '100K',
    10: 'Max'
}


def get_component(df: pd.DataFrame):

    dropdown_options = list(df['estate'].unique())

    component = dbc.Row(
        [
            html.H3(
                'Price vs. Area with Price per Square Meter by Room Count',
                style={'padding-bottom': '10px'}
            ),
            dbc.Row([
                dbc.Col(
                    [
                        dcc.Dropdown(
                            dropdown_options,
                            value=None,
                            id='estate-type-scatter',
                            placeholder='Select Type of Property',
                            style={
                                'color': 'black',
                                'backgroundColor': 'white',
                            },
                        ),
                    ],
                    md=3
                ),
                dbc.Col(
                    [
                        dcc.Checklist(
                            options={
                                'log_x': 'Log X Axis',
                                'log_y': 'Log Y Axis',
                            },
                            value=['log_x', 'log_y'],
                            inline=True,
                            id='log-axis',
                        )
                    ],
                    md=3
                ),
                dcc.Graph(id='scatter-figure'),
                html.Div([
                    html.P('Area Slider'),
                    dcc.RangeSlider(1, 10,
                        marks=AREA_MARKS_LABELS,
                        value=[1, 10],
                        dots=False,
                        step=None,
                        allowCross=False,
                        updatemode='drag',
                        id='area-mark',
                    ),
                ])
            ])
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


@app.callback(
    Output('scatter-figure', 'figure'),
    Input('estate-type-scatter', 'value'),
    Input('log-axis', 'value'),
    Input('area-mark', 'value')
)
def scatter_plot(estate_type, log_axis, area_mark):

    df = Data().get_data()

    ''' Area range filter'''
    map_marks = {
        1: df.areaInSquareMeters.min(),
        2: 30,
        3: 50,
        4: 100,
        5: 150,
        6: 500,
        7: 1000,
        8: 10_000,
        9: 100_000,
        10: df.areaInSquareMeters.max()
    }

    min_range_selected = area_mark[0]
    max_range_selected = area_mark[1]

    min_area = map_marks[min_range_selected]
    max_area = map_marks[max_range_selected]

    df_filtered = df[
        (df.areaInSquareMeters >= min_area) &
        (df.areaInSquareMeters <= max_area)
    ]

    ''' Type of property filter (estate)'''
    if estate_type:
        df_filtered = df_filtered[df_filtered['estate'] == estate_type]

    color_scale = px.colors.sequential.Viridis
    color_map = {f'T{i}': color_scale[i] for i in range(10)}
    color_map['T9+'] = color_scale[-1]

    '''Figure plot'''
    fig = px.scatter(
        df_filtered,
        y='totalPrice',
        x='areaInSquareMeters',
        size='pricePerSquareMeter',
        color='roomsNumberNotation',
        color_discrete_map=color_map,
    )

    '''Log axis filter'''
    fig.update_xaxes(type='log' if 'log_x' in log_axis else 'linear')
    fig.update_yaxes(type='log' if 'log_y' in log_axis else 'linear')

    fig.update_layout(
        transition_duration=500,
        margin=dict(l=0, r=0, t=20, b=0),
        paper_bgcolor='rgba(0, 0, 0, 0)',
        plot_bgcolor='rgba(0, 0, 0, 0)',
        font=dict(color='white'),
        xaxis_title='Area (m²)',
        yaxis_title='Price (€)',
    )

    return fig
