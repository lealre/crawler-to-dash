
from dash import Dash, html
import dash_bootstrap_components as dbc


app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = dbc.Container(
    [
        dbc.Row([
            dbc.Col(html.P('Col 1'), width= 6, style={'background-color': 'green'}),
            dbc.Col(html.P('Col 2'), style={'background-color': 'yellow'}),
            dbc.Col(html.P('Col 3'), style={'background-color': 'red'}),
        ])

    ],
    style = {'max-width': '100%'}
    # dbc.Alert("Hello Bootstrap!", color="success"),
    # className="p-5",
    
)


if __name__=='__main__':
    app.run_server(debug=True)