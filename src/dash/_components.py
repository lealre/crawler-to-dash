import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Input, Output, dash_table, dcc, html

from src.dash.components.app import app
from src.dash.data import Data

df = Data().get_data()


def heatmap_component():
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
            colorbar=dict(title='Price per Square Meter'),
            zmin=pivot_df.values.min(),
            zmax=pivot_df.values.max(),
            text=pivot_df.values,
            texttemplate='%{text:.2f}',
            textfont=dict(size=12, color='black'),
        )
    )

    heatmap.update_layout(
        title='Heatmap of Price per Square Meter',
        xaxis_title='Location',
        yaxis_title='Rooms Number Notation',
    )

    component = dbc.Row([
        html.H2(
            'Price per m2 - Location x Rooms Number',
            style={'padding-bottom': '20px'},
        ),
        dcc.Graph(figure=heatmap),
    ])

    return component


def proportion_component():
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


def table():

    data = {
    'location': ['Alenquer', 'Amadora', 'Arruda Dos Vinhos', 'Azambuja', 'Cadaval', 'Cascais', 'Lisboa', 'Loures',
                 'Lourinha', 'Mafra', 'Odivelas', 'Oeiras', 'Sintra', 'Sobral De Monte Agraco', 'Torres Vedras', 'Vila Franca De Xira'],
    'mean': [2691.0, 123.0, 2453.0, 8036.0, 2401.0, 218.0, 259.0, 659.0, 264.0, 1269.0, 146.0, 251.0, 1185.0, 8351.0, 1467.0, 3056.0],
    'median': [138.0, 82.0, 126.0, 131.0, 170.0, 173.0, 96.0, 126.0, 164.0, 154.0, 114.0, 134.0, 114.0, 142.0, 172.0, 120.0],
    'max': [210000.0, 15130.0, 200000.0, 287920.0, 160000.0, 10000.0, 200000.0, 140000.0, 48960.0, 481937.0, 1850.0, 10470.0, 429000.0, 260199.0, 270000.0, 369158.0],
    'min': [12.0, 25.0, 43.0, 35.0, 34.0, 17.0, 12.0, 31.0, 24.0, 25.0, 34.0, 27.0, 26.0, 35.0, 14.0, 35.0]
    }

    example_data = pd.DataFrame(data)

    df_grouped = df.groupby('location').agg({
    'areaInSquareMeters': ['mean', 'median', 'max', 'min'],
    }).round(0)

    component = dbc.Col([
        dash_table.DataTable(
            data=example_data.to_dict('records'),  # Convert DataFrame to dict
            columns=[{'name': col, 'id': col} for col in example_data.columns],  # Define columns
        )
    ], md=3)

    return component


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
        size='totalPrice',
        log_x=True,
        log_y=True,
    )

    return fig
