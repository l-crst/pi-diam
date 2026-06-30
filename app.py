from main import *
from dash import Dash, html, dcc, callback, Output, Input
import dash_ag_grid as dag
import plotly.express as px
import dash_bootstrap_components as dbc


# Initialize the app
app = Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])

# App layout
app.layout = dbc.Container(
    [
        html.H1('Analyse du cycle de vie des clients de la société DIAM Bouchage'),
        html.Hr(),
        dcc.RadioItems(
            options=['dépenseClient', 'nbCommandesClient','commandesAn'],
            value='dépenseClient',
            id='radio-item',
            inline=True),

        dbc.Row(
    [
                dbc.Col(dcc.Graph(figure={}, id='graph'), md=8),
                dbc.Col(dcc.Graph(figure={}, id='side-graph'), md=4),
            ],
            align='center',
        ),
    ],
    fluid=True,
)

# Add controls to build the interaction
@callback(
    Output(component_id='graph', component_property='figure'),
    Input(component_id='radio-item', component_property='value')
)
def update_graph(graph_type):
    if graph_type == 'dépenseClient':
        fig = px.histogram(df.groupby('nom_client')['CA_EUR'].sum().reset_index(name='total_depense'), x='nom_client', y='total_depense')
    elif graph_type == 'nbCommandesClient':
        fig = px.histogram(df.groupby('nom_client').size().reset_index(name='nb_commandes'), x='nom_client', y='nb_commandes')
    elif graph_type == 'commandesAn':
        fig = px.line(df.groupby('annee').size().reset_index(name='nb_commandes'), x='annee', y='nb_commandes')

    return fig


@callback(
    Output('side-graph', 'figure'),
    Input('graph','hoverData'),
    Input('radio-item','value'),
)
def update_side_graph(hoverData, graph_type):
    if hoverData is None or graph_type=='commandesAn':
        fig = None

    if graph_type == 'dépenseClient' or graph_type == 'nbCommandesClient':
        client = hoverData['points'][0]['x']
        filtered_df = df[df['nom_client'] == client].groupby('gamme').size().reset_index(name='number')
        fig = px.pie(filtered_df, names='gamme', values='number', title=f'Répartition des gammes pour le client {client}')

    return fig

# Run the app
if __name__ == '__main__':
    app.run(debug=True)