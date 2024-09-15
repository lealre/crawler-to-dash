import dash_bootstrap_components as dbc

from src.dash.components.app import app
from src.dash.components.body.body import Body
from src.dash.components.head.head import Head

head = Head()
body = Body()

app.layout = dbc.Container(
    [head.component, body.component],
    fluid=True,
    style={
        'width': '100%',
        'padding': '15px 25px 25px 25px',
        'background-color': '#191c24',
    },
)


if __name__ == '__main__':
    app.run_server(debug=True, port=8051)
