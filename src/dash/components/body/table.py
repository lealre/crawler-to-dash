from dash import dash_table, html

from src.dash.components.app import df


def get_component():
    df_agg = (
        df.groupby('location')
        .agg({
            'totalPrice': ['mean', 'median'],
        })
        .round(0)
    )

    df_agg.columns = df_agg.columns.droplevel(0)
    
    df_agg = df_agg.reset_index()

    df_agg.columns = ['Location', 'Mean (€)', 'Median (€)']


    component = dash_table.DataTable(
        data=df_agg.to_dict('records'),
        columns=[{'name': col, 'id': col} for col in df_agg.columns],
        id='table-mask',
        style_header={
            'backgroundColor': '#222729',
            'fontWeight': 'bold',
            'border': '0px',
            'font-size': '15px',
            'color': '#D3D6DF',
        },
        style_cell={
            'textAlign': 'center',
            'padding': '12px 8px',
            'backgroundColor': '#131516',
            'color': '#D3D6DF',
        },
        style_data={'border': '0px', 'font-size': '15x'},
        style_table={
            'borderRadius': '8px',
            'overflow': 'hidden',
            'border': '2px solid #222729',
            'overflowX': 'auto',
            'maxWidth': '100%', 
        },
    )

    return component