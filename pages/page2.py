import dash
from main import *
from dash import html, dcc, callback, Input, Output
import plotly.express as px
import dash_bootstrap_components as dbc

dash.register_page(__name__,name="Analyse des gammes")

layout = html.Div([
    html.H1("page 2")
])

options = [
    {'label': 'Répartition des gammes', 'value': 'gammes'},
    {'label': 'Évolution des gammes', 'value': 'evolutionGammes'},
    {'label': 'Évolution du CA par gamme', 'value': 'evolutionGammesCA'},#les boutons

]
# truc classique pour les pages
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
                    id='radio-item-gammes',
                    options=options,
                    value='gammes',
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
                dcc.Graph(figure={}, id='graph-gammes'),
            ],
            align='center',
        ),
    ],
    fluid=True,
)

# Le contenu de la page
@callback(
    Output(component_id='graph-gammes', component_property='figure'),
    Input(component_id='radio-item-gammes', component_property='value')
)
def update_graph(graph_type):
    if graph_type == 'gammes':
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

