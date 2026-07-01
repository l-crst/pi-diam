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
    {'label': 'CA/Récence', 'value': 'CA/Récence'},
    {'label': 'Répartition des gammes', 'value': 'gammes'},
    {'label': 'Évolution des gammes', 'value': 'evolutionGammes'},
    {'label': 'Évolution du CA par gamme', 'value': 'evolutionGammesCA'},
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
                    id='radio-item',
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
    elif graph_type  == "CA/Récence":
        couleurs = {
            "Champions (à chouchouter)": "#2ecc71",
            "Gros clients perdus (à réactiver)": "#e74c3c",
            "Petits clients actifs (à développer)": "#3498db",
            "Petits clients inactifs (à surveiller)": "#95a5a6"
        }

        fig = px.scatter(
            client_df,
            x="jours_inactif",
            y="total_ca",
            color="segment",
            size="nb_commandes",  # Plotly gère la taille automatiquement
            size_max=60,
            color_discrete_map=couleurs,
            opacity=0.6,
            title="Segmentation clients — CA vs Récence<br>(taille du point = nb de commandes)",
            labels={
                "jours_inactif": "Jours depuis la dernière commande",
                "total_ca": "CA total (€)",
                "segment": "Segment"
            },
            hover_data=["nom_client"]

        )

        # 2. Ajout du contour blanc sur les points (équivalent edgecolors="white")
        fig.update_traces(
            marker=dict(line=dict(width=0.4, color='white')),
            selector=dict(mode='markers')
        )

        # 3. Lignes de séparation des quadrants
        fig.add_vline(x=seuil_recence, line_dash="dash", line_color="grey", line_width=1)
        fig.add_hline(y=seuil_ca, line_dash="dash", line_color="grey", line_width=1)

        max_ca = client_df["total_ca"].max()

        fig.add_annotation(x=50, y=max_ca * 0.9, text="<b>CHAMPIONS<br>à chouchouter</b>",
                           font=dict(color="#2ecc71", size=12), showarrow=False)
        fig.add_annotation(x=400, y=max_ca * 0.9, text="<b>GROS CLIENTS PERDUS<br>à réactiver d'urgence</b>",
                           font=dict(color="#e74c3c", size=12), showarrow=False)
        fig.add_annotation(x=50, y=seuil_ca * 0.1, text="Petits clients<br>actifs", font=dict(color="#3498db", size=10),
                           showarrow=False)
        fig.add_annotation(x=400, y=seuil_ca * 0.1, text="Petits clients<br>inactifs",
                           font=dict(color="#95a5a6", size=10), showarrow=False)

        # 5. Formatage final (axes, dimensions, thème)
        fig.update_layout(
            yaxis=dict(tickformat="s", ticksuffix="€"),  # Transforme automatiquement "1000" en "1k€"
            template="plotly_white",  # Thème épuré proche de Matplotlib
            width=1000,
            height=650,
            legend_title_text="",  # Enlève le titre "segment" au-dessus de la légende pour faire plus propre
            legend=dict(yanchor="top", y=0.99, xanchor="right", x=0.99)  # Positionnement de la légende
        )

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

