import dash_bootstrap_components as dbc
from dash import Dash

from src.dash.data import Data

df = Data.get_data()

app = Dash(external_stylesheets=[dbc.themes.DARKLY])
