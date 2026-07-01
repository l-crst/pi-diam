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
            options=['dépenseClient', 'nbCommandesClient','commandesAn','panierMoyen','gammes','evolutionGammes', 'evolutionGammesCA'],
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
        fig = px.histogram(df.groupby('nom_client')['CA_EUR'].sum().reset_index(name='total_depense'), x='nom_client', y='total_depense')
    elif graph_type == 'nbCommandesClient':
        fig = px.histogram(df.groupby('nom_client').size().reset_index(name='nb_commandes'), x='nom_client', y='nb_commandes')
    elif graph_type == 'commandesAn':
        fig = px.line(df.groupby('annee').size().reset_index(name='nb_commandes'), x='annee', y='nb_commandes')
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
    elif graph_type == 'gammes':
        fig = px.histogram(df.groupby('gamme')['CA_EUR'].sum().reset_index(name='total_depense'), x='gamme', y='total_depense')
    elif graph_type == 'evolutionGammes':
        df_plot = tableau_graph.reset_index().melt(
            id_vars='rang_commande',
            var_name='Gamme',
            value_name='pct'
        )
        fig = px.area(
            df_plot,
            x='rang_commande',
            y='pct',
            color='Gamme',
            groupnorm='percent',
            title="Évolution de la répartition des commandes par gamme selon l'ancienneté du client"
        )
        fig.update_layout(
            xaxis_title="Rang de la commande (1 = première commande)",
            yaxis_title="Répartition des commandes par gamme (%)",
            legend_title="Gamme"
        )

    elif graph_type == 'evolutionGammesCA':
        df_plot_ca = tableau_graph_ca.reset_index().melt(
            id_vars='rang_commande',
            var_name='Gamme',
            value_name='pct_ca'
        )
        fig = px.area(
            df_plot_ca,
            x='rang_commande',
            y='pct_ca',
            color='Gamme',
            groupnorm='percent',
            title="Évolution de la répartition du chiffre d'affaires par gamme selon l'ancienneté du client"
        )
        fig.update_layout(
            xaxis_title="Rang de la commande (1 = première commande)",
            yaxis_title="Répartition du chiffre d'affaires par gamme (%)",
            legend_title="Gamme"
        )
    return fig

# Run the app
if __name__ == '__main__':
    app.run(debug=True)