from main import *
import dash
from dash import Dash, html, dcc, callback, Output, Input
import dash_ag_grid as dag
import plotly.express as px
import dash_bootstrap_components as dbc




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
        html.P("A simple sidebar layout with navigation links", className="lead"),
        html.Div([
            html.Div(
                dcc.Link(f"{page['name']} - {page['path']}", href=page["relative_path"])
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

# Run the app
if __name__ == '__main__':
    app.run(debug=True)