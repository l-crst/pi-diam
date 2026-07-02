import dash
from main import *
from dash import html, dcc, callback, Input, Output
import plotly.express as px
import dash_bootstrap_components as dbc
import dash_ag_grid as dag

dash.register_page(__name__, name="Analyse des clients")

options = [
    {'label': 'Dépense Client', 'value': 'dépenseClient'},
    {'label': 'Nb Commandes Client', 'value': 'nbCommandesClient'},
    {'label': 'Commandes / An', 'value': 'commandesAn'},
    {'label': 'Ancienneté des clients', 'value': 'Ancienneté des clients'},
    {'label': 'Panier moyen', 'value': 'panierMoyen'},
    {'label': 'Clients à surveiller', 'value': 'clientsSurveiller'},
    {'label': 'Clients par an', 'value': 'clientsParAn'},  # <-- nouvel onglet
]

# ------------------------------------------------------------------
# Préparation des données pour l'onglet "Clients par an"
# ------------------------------------------------------------------
clients_par_an = (
    df.dropna(subset=['annee'])
    .groupby('annee')['nom_client']
    .nunique()
    .reset_index(name='nb_clients')
    .sort_values('annee')
    .reset_index(drop=True)
)
clients_par_an['delta_abs'] = clients_par_an['nb_clients'].diff()
clients_par_an['delta_pct'] = (clients_par_an['nb_clients'].pct_change() * 100).round(1)
clients_par_an['annee'] = clients_par_an['annee'].astype(int)

# Colonnes formatées pour l'affichage (le calcul de couleur se base sur parseFloat, donc le "+"/"%" ne gêne pas)
clients_par_an['delta_abs_fmt'] = clients_par_an['delta_abs'].apply(
    lambda x: '-' if pd.isna(x) else f"{int(x):+d}"
)
clients_par_an['delta_pct_fmt'] = clients_par_an['delta_pct'].apply(
    lambda x: '-' if pd.isna(x) else f"{x:+.1f}%"
)

# Règle de couleur commune : vert si positif, rouge si négatif, neutre sinon (première année)
style_couleur_delta = {
    "styleConditions": [
        {"condition": "parseFloat(params.value) > 0", "style": {"color": "#1e7e34", "fontWeight": "bold"}},
        {"condition": "parseFloat(params.value) < 0", "style": {"color": "#c0392b", "fontWeight": "bold"}},
    ],
    "defaultStyle": {"color": "#6c757d"},
}

table_clients_par_an = dag.AgGrid(
    id='grid-clients-par-an',
    columnDefs=[
        {"field": "annee", "headerName": "Année", "sortable": True, "filter": True},
        {"field": "nb_clients", "headerName": "Nb clients", "sortable": True, "filter": True},
        {"field": "delta_abs_fmt", "headerName": "Delta vs N-1", "cellStyle": style_couleur_delta},
        {"field": "delta_pct_fmt", "headerName": "Delta %", "cellStyle": style_couleur_delta},
    ],
    rowData=clients_par_an.to_dict('records'),
    defaultColDef={"resizable": True, "sortable": True, "filter": True},
    dashGridOptions={"domLayout": "autoHeight"},
    style={"width": "100%"},
    className="ag-theme-alpine",
    dangerously_allow_code=True,  # nécessaire pour les cellStyle avec condition JS (parseFloat)
# Calcul des valeurs à afficher (chiffres fixes, pas besoin de callback)
nb_mono = int((analyse['type_client'] == 'Mono-gamme').sum())
nb_multi = int((analyse['type_client'] == 'Multi-gamme').sum())
pct_mono = repartition_clients.get('Mono-gamme', 0)
pct_multi = repartition_clients.get('Multi-gamme', 0)

pct_ca_mono = stats_par_type.loc['Mono-gamme', '%_CA_total'] if 'Mono-gamme' in stats_par_type.index else 0
pct_ca_multi = stats_par_type.loc['Multi-gamme', '%_CA_total'] if 'Multi-gamme' in stats_par_type.index else 0

depense_moyenne_mono = stats_par_type.loc['Mono-gamme', 'depense_moyenne'] if 'Mono-gamme' in stats_par_type.index else 0
depense_moyenne_multi = stats_par_type.loc['Multi-gamme', 'depense_moyenne'] if 'Multi-gamme' in stats_par_type.index else 0

kpi_mono_multi = dbc.Row(
    [
        dbc.Col(
            dbc.Card(
                dbc.CardBody([
                    html.H4("Mono-gamme", className="card-title"),
                    html.P(f"{nb_mono} clients ({pct_mono}%)", className="card-text"),
                    html.P(f"{pct_ca_mono}% du CA total", className="card-text text-muted"),
                    html.P(f"Dépense moyenne : {depense_moyenne_mono:,.0f} €", className="card-text text-muted"),
                ]),
                color="light",
            ),
            width=6,
        ),
        dbc.Col(
            dbc.Card(
                dbc.CardBody([
                    html.H4("Multi-gamme", className="card-title"),
                    html.P(f"{nb_multi} clients ({pct_multi}%)", className="card-text"),
                    html.P(f"{pct_ca_multi}% du CA total", className="card-text text-muted"),
                    html.P(f"Dépense moyenne : {depense_moyenne_multi:,.0f} €", className="card-text text-muted"),
                ]),
                color="light",
            ),
            width=6,
        ),
    ],
    className="mb-4",
)

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

        kpi_mono_multi,

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
                dbc.Col(dcc.Graph(figure={}, id='graph-clients'), width=7, id='graph-clients-container'),
                dbc.Col(
                    dcc.Graph(figure={}, id='side-graph-clients'),
                    id='side-graph-clients-container',
                    md=4,
                    style={'display': 'none'},
                ),
            ],
            align='center',
        ),

        # Onglet "Clients par an" : caché par défaut, affiché via callback
        dbc.Row(
            dbc.Col(table_clients_par_an, width=8, id='table-clients-container', style={'display': 'none'}),
            justify='center',
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
    if graph_type == 'clientsParAn':
        # Pas de graphe pour cet onglet, le tableau prend le relais
        return {}
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
    elif graph_type == 'clientsSurveiller':
        df_alerte = clients_a_surveiller[clients_a_surveiller['statut'] == 'À surveiller'].head(20)
        fig = px.bar(
            df_alerte,
            x='nom_client',
            y='ratio',
            color='ca_total',
            color_continuous_scale='Reds',
            title="Top 20 clients à surveiller (rythme d'achat ralenti)"
        )
        fig.update_layout(
            xaxis_title="Client",
            yaxis_title="Ratio inactivité / rythme habituel",
            xaxis_tickangle=-45
        )
    return fig


# Bascule d'affichage : graphe (+ side-graph) vs tableau "Clients par an"
@callback(
    Output('graph-clients-container', 'style'),
    Output('table-clients-container', 'style'),
    Input('radio-item-clients', 'value'),
)
def toggle_vue_clients_par_an(graph_type):
    if graph_type == 'clientsParAn':
        return {'display': 'none'}, {'display': 'block'}
    return {'display': 'block'}, {'display': 'none'}


@callback(
    Output('side-graph-clients', 'figure'),
    Output('side-graph-clients-container', 'style'),
    Output('graph-clients-container', 'md'),  # <-- Nouvel Output pour redimensionner la colonne principale
    Input('graph-clients', 'hoverData'),
    Input('radio-item-clients', 'value'),
)
def update_side_graph(hoverData, graph_type):
    # Si on ne survole rien OU que le graphe n'utilise pas le side-graph
    if hoverData is None or graph_type not in ['dépenseClient', 'nbCommandesClient']:
        # Fig vide, colonne cachée, ET la colonne principale prend 12 espaces (100%)
        return {}, {'display': 'none'}, 12

    # Si on est dans un cas où le side-graph doit s'afficher :
    if graph_type in ['dépenseClient', 'nbCommandesClient']:
        client = hoverData['points'][0]['x']
        filtered_df = df[df['nom_client'] == client].groupby('gamme').size().reset_index(name='number')
        fig = px.pie(filtered_df, names='gamme', values='number',
                     title=f'Répartition des gammes pour le client {client}')

        # Fig calculée, colonne visible, ET la colonne principale se réduit à 8 espaces
        return fig, {'display': 'block'}, 8
        return fig, {'display': 'block'}, 8
