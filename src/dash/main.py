import dash_bootstrap_components as dbc

from src.dash.components.head.head import Head
from src.dash.components.body.body import Body
from src.dash.components.app import app

head = Head()
body = Body()

app.layout = dbc.Container(
    [head.component, body.component],
    fluid = True,
    style = {
        # 'height': '100vh', 
        'width': '100%', 
        'padding': "25px 25px 0px 25px",
        'background-color': '#191C24'
    },
)


if __name__ == "__main__":
    app.run_server(debug = True, port = 8051)
