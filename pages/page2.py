import dash
from main import *
from dash import html, dcc, callback, Input, Output
import plotly.express as px
import dash_bootstrap_components as dbc

dash.register_page(__name__)

layout = html.Div([
    html.H1("page 2")
])