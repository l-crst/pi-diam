from main import *
from dash import Dash, html, dcc, callback, Output, Input
import dash_ag_grid as dag
import pandas as pd
import plotly.express as px
import dash_bootstrap_components as dbc


# Initialize the app
external_stylesheets = [dbc.themes.CERULEAN]
app = Dash(__name__, external_stylesheets=external_stylesheets)

# App layout
app.layout = dbc.Container(
    [
        html.H1('My First App with Data and a Graph'),
        html.Hr(),
        dcc.RadioItems(
            options=['dépenseClient', 'nbCommandesClient','commandesAn'],
            value='dépenseClient',
            id='controls-and-radio-item',
            inline=True),

        dbc.Row(
    [
                dbc.Col(dag.AgGrid(rowData=df.to_dict('records'),columnDefs=[{"field": i} for i in df.columns]), md=4),
                dbc.Col(dcc.Graph(figure={}, id='controls-and-graph'), md=8),
            ],
            align='center',
        ),
    ],
    fluid=True,
)

# Add controls to build the interaction
@callback(
    Output(component_id='controls-and-graph', component_property='figure'),
    Input(component_id='controls-and-radio-item', component_property='value')
)
def update_graph(graph_type):
    if graph_type == 'dépenseClient':
        fig = px.histogram(classement, x='nom_client', y='total_depense')
    elif graph_type == 'nbCommandesClient':
        fig = px.histogram(df.groupby('nom_client').size().reset_index(name='nb_commandes'), x='nom_client', y='nb_commandes')
    elif graph_type == 'commandesAn':
        fig = px.line(df.groupby('annee').size().reset_index(name='nb_commandes'), x='annee', y='nb_commandes')

    return fig

# Run the app
if __name__ == '__main__':
    app.run(debug=True)