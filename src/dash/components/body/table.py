import pandas as pd
from dash import dash_table


def get_component(df: pd.DataFrame):
    df_agg = df.groupby('location').agg({
        'areaInSquareMeters': ['mean', 'median'],
    }).round(0)

    df_agg.columns = df_agg.columns.droplevel(0)

    df_agg = df_agg.reset_index()

    component = dash_table.DataTable(
        data=df_agg.to_dict('records'),
        columns=[{'name': col, 'id': col} for col in df_agg.columns],
        id='table-mask',
        style_header={
            'backgroundColor': '#222729',
            'fontWeight': 'bold',
            'border': '0px',
            'font-size': "15px",
            'color': '#D3D6DF'
        },
        style_cell={
            'textAlign': 'center',
            'padding': '12px 8px',
            'backgroundColor': '#131516',
            'color': '#D3D6DF'
        },
        style_data={
            'border': '0px',
            'font-size': "15x"},
        style_table={
            'borderRadius': '8px',
            "overflow": "hidden",
            'border': '2px solid #222729'
        },
    )

    return component

# @app.callback(
#     Input(...),
#     Output('table-mask', 'data')
# )
# def table():

#     df = Data().get_data()

#     df_agg = df.groupby('location').agg({
#         'areaInSquareMeters': ['mean', 'median'],
#     }).round(0)

#     df_agg.columns = df_agg.columns.droplevel(0)

#     df_agg = df_agg.reset_index()
