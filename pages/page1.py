import dash
from main import *
from dash import html, dcc, callback, Input, Output
import plotly.express as px
import dash_bootstrap_components as dbc

dash.register_page(__name__)

options = [
    {'label': 'Dépense Client', 'value': 'dépenseClient'},
    {'label': 'Nb Commandes Client', 'value': 'nbCommandesClient'},
    {'label': 'Commandes / An', 'value': 'commandesAn'},
    {'label': 'Ancienneté des clients', 'value': 'Ancienneté des clients'},
    {'label': 'Panier moyen', 'value': 'panierMoyen'},
]
# App layout
layout = dbc.Container(
    [
              html.Div(
            [
                html.H1(
                    'Analyse du cycle de vie des clients de la société DIAM Bouchage',
                    className='text-center',
                ),
            ],
            style={'marginTop': '40px', 'marginBottom': '30px'},
        ),
        html.Hr(),
        dbc.Row(
            dbc.Col(
                dbc.RadioItems(
                    id='radio-item-clients',
                    options=options,
                    value='dépenseClient',
                    inline=True,
                    className='btn-group',
                    inputClassName='btn-check',
                    labelClassName='btn btn-outline-primary',
                    labelCheckedClassName='active',
                ),
                width='auto',
            ),
            justify='center',
            className='mb-4',
        ),

        dbc.Row(
    [
                dbc.Col(dcc.Graph(figure={}, id='graph-clients'), md=8),
                dbc.Col(dcc.Graph(figure={}, id='side-graph-clients'), md=4),
            ],
            align='center',
        ),
    ],
    fluid=True,
)

# Add controls to build the interaction
@callback(
    Output(component_id='graph-clients', component_property='figure'),
    Input(component_id='radio-item-clients', component_property='value')
)
def update_graph(graph_type):
    if graph_type == 'dépenseClient':
        fig = px.histogram(df.groupby('nom_client')['CA_EUR'].sum().reset_index(name='total_depense'), x='nom_client', y='total_depense')
    elif graph_type == 'nbCommandesClient':
        fig = px.histogram(df.groupby('nom_client').size().reset_index(name='nb_commandes'), x='nom_client', y='nb_commandes')
    elif graph_type == 'commandesAn':
        fig = px.line(df.groupby('annee').size().reset_index(name='nb_commandes'), x='annee', y='nb_commandes')
    elif graph_type == "Ancienneté des clients":
        df_pie = repartition.reset_index()
        df_pie.columns = ["Anciennete", "Valeur"]
        fig = px.pie(
            df_pie,
            names="Anciennete",
            values="Valeur",
            title="Répartition de l'ancienneté des clients",
            color_discrete_sequence=["#ff9999", "#66b3ff", "#99ff99", "#ffcc99", "#c2c2f0"],
        )
        fig.update_traces(textinfo="percent+label")
   
    elif graph_type == 'panierMoyen':
        evolution_plot = evolution_panier_moyen.copy()
        evolution_plot['mois'] = evolution_plot['mois'].astype(str)
        fig = px.line(
            evolution_plot,
            x='mois',
            y='panier_moyen',
            markers=True,
            title="Évolution du panier moyen dans le temps"
        )
        fig.update_layout(
            xaxis_title="Mois",
            yaxis_title="Panier moyen (EUR)",
            xaxis_tickangle=-90
        ) 




@callback(
    Output('side-graph-clients', 'figure', allow_duplicate=True),
    Input('graph-clients','hoverData'),
    Input('radio-item-clients','value'),
    prevent_initial_call=True,
)
def update_side_graph(hoverData, graph_type):
    if hoverData is None or graph_type=='commandesAn':
        fig = None

    if graph_type == 'dépenseClient' or graph_type == 'nbCommandesClient':
        client = hoverData['points'][0]['x']
        filtered_df = df[df['nom_client'] == client].groupby('gamme').size().reset_index(name='number')
        fig = px.pie(filtered_df, names='gamme', values='number', title=f'Répartition des gammes pour le client {client}')

    return fig

