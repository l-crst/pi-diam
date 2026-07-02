from main import *
import dash
from dash import Dash, html, dcc, callback, Output, Input
import dash_ag_grid as dag
import plotly.express as px
import dash_bootstrap_components as dbc

import webbrowser
from threading import Timer




# Initialize the app
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], use_pages=True)

SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "16rem",
    "padding": "2rem 1rem",
    "background-color": "#f8f9fa",
}

CONTENT_STYLE = {
    "margin-left": "18rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem",
}

sidebar = html.Div(
    [
        html.H2("Sidebar", className="display-4"),
        html.Hr(),
        html.P("Analyse de différents aspects (clients,gamme, international)", className="lead"),
        html.Div([
            html.Div(
                dcc.Link(f"{page['name']}", href=page["relative_path"])
            ) for page in dash.page_registry.values()
        ]),
    ],
    style=SIDEBAR_STYLE,)

content = html.Div([
    dash.page_container,
    ]
    , style=CONTENT_STYLE)

# App layout
app.layout = html.Div([dcc.Location(id="url"), sidebar, content])


def open_browser():
    # Ouvre l'URL par défaut de Dash dans le navigateur web
    webbrowser.open_new("http://127.0.0.1:8050/page1")


if __name__ == '__main__':
    Timer(1.5, open_browser).start()
    app.run(debug=False, port=8050)