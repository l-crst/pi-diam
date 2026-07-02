# pour la nouvelle data a l'international

import dash
from main import *
from dash import html, dcc, callback, Input, Output, dash_table
import plotly.express as px
import dash_bootstrap_components as dbc
import pandas as pd
import numpy as np
import pycountry

dash.register_page(__name__, name="International")

# --- CHARGEMENT DES DONNÉES ---
df_intl = pd.read_csv("VfinaleHIstorical Sales(Copie de Sheet1) (1).csv", sep=";")

# --- NETTOYAGE / TYPAGE ---
df_intl['Date_Fact'] = pd.to_datetime(df_intl['Date_Fact'], errors='coerce')


def nettoyer_quantite(val):
    """
    Nettoie une valeur numérique au format français (espaces, virgules,
    séparateurs de milliers) et la convertit en float.
    """
    if pd.isna(val):
        return None
    val = str(val).strip()
    val = val.replace('\xa0', '').replace(' ', '')  # espaces normaux + insécables
    if val == '':
        return None
    if ',' in val:
        val = val.replace('.', '').replace(',', '.')
    try:
        return float(val)
    except ValueError:
        return None


df_intl['QUANTITE'] = df_intl['QUANTITE'].apply(nettoyer_quantite)
df_intl = df_intl.dropna(subset=['Date_Fact', 'PAYS_FACT'])
df_intl['annee'] = df_intl['Date_Fact'].dt.year


def convertir_iso2_en_iso3(code_iso2):
    if pd.isna(code_iso2):
        return None
    code = str(code_iso2).strip().upper()
    corrections = {"UK": "GB", "EL": "GR"}
    code = corrections.get(code, code)
    try:
        pays = pycountry.countries.get(alpha_2=code)
        return pays.alpha_3 if pays else None
    except Exception:
        return None


df_intl['iso_alpha3'] = df_intl['PAYS_FACT'].apply(convertir_iso2_en_iso3)

# --- AGRÉGAT ANNUEL PAR PAYS (utilisé pour panier moyen, fréquence, variations) ---
df_yearly = (
    df_intl.groupby(['PAYS_FACT', 'iso_alpha3', 'annee'])
    .agg(
        quantite_totale=('QUANTITE', 'sum'),
        nb_commandes=('Code_Client', 'count'),
    )
    .reset_index()
)
df_yearly['panier_moyen'] = df_yearly['quantite_totale'] / df_yearly['nb_commandes']
df_yearly['frequence'] = df_yearly['nb_commandes']  # nombre de commandes sur l'année

# --- OPTIONS DU RADIO ---
options = [
    {'label': 'Répartition géographique des clients', 'value': 'geoclients'},
    {'label': 'Évolution des commandes par pays', 'value': 'evolutionPays'},
    {'label': 'Top pays par quantité', 'value': 'topPays'},
    {'label': 'Évolution du panier moyen par pays', 'value': 'panierMoyen'},
]

# --- OPTIONS DU MENU DÉROULANT (ANNÉES) ---
annees_disponibles = sorted(df_intl['annee'].dropna().unique().astype(int).tolist())
derniere_annee_globale = max(annees_disponibles)
options_annee = [{'label': 'Total (toutes années)', 'value': 'total'}] + [
    {'label': str(a), 'value': a} for a in annees_disponibles
]

# Boutons pour lesquels le menu déroulant Année est pertinent
boutons_avec_filtre_annee = ('geoclients', 'topPays', 'panierMoyen')

# --- MISE EN PAGE (LAYOUT) ---
layout = dbc.Container(
    [
        html.Div(
            [
                html.H1(
                    "Analyse internationale des ventes - DIAM Bouchage",
                    className='text-center',
                ),
            ],
            style={'marginTop': '40px', 'marginBottom': '30px'},
        ),
        html.Hr(),
        dbc.Row(
            dbc.Col(
                dbc.RadioItems(
                    id='radio-item-pays',
                    options=options,
                    value='geoclients',
                    inline=True,
                    className='btn-group',
                    inputClassName='btn-check',
                    labelClassName='btn btn-outline-primary',
                    labelCheckedClassName='active',
                ),
                width='auto',
            ),
            justify='center',
            className='mb-3',
        ),

        # --- Menu déroulant Année (visible pour boutons 1, 3 et 4) ---
        dbc.Row(
            dbc.Col(
                html.Div(
                    id='container-dropdown-annee',
                    children=[
                        dcc.Dropdown(
                            id='dropdown-annee',
                            options=options_annee,
                            value='total',
                            clearable=False,
                            style={'width': '250px'},
                        ),
                    ],
                    style={'display': 'block'},
                ),
                width='auto',
            ),
            justify='center',
            className='mb-4',
        ),

        dbc.Row(
            [
                dcc.Loading(
                    id="loading-carte",
                    type="default",
                    children=dcc.Graph(figure={}, id='graph-pays', style={"height": "650px"}),
                ),
            ],
            align='center',
        ),

        # --- Section texte + image (visible uniquement pour "geoclients") ---
        html.Div(
            id='section-carte-vins',
            children=[
                html.Hr(),
                html.Div(
                    "Texte à compléter ici : commentaire sur la répartition géographique des clients.",
                    style={
                        'padding': '20px',
                        'fontSize': '16px',
                        'textAlign': 'justify',
                    },
                ),
                html.Img(
                    src="/assets/carte_vins.jpeg",
                    style={
                        'width': '100%',
                        'maxWidth': '900px',
                        'display': 'block',
                        'margin': '20px auto',
                    },
                ),
            ],
            style={'display': 'block'},
        ),

        # --- Section tableau de classement (visible uniquement pour "panierMoyen") ---
        html.Div(
            id='section-table-panier',
            children=[
                html.Hr(),
                html.H4("Classement des pays par panier moyen", className='text-center', style={'marginBottom': '20px'}),
                dash_table.DataTable(
                    id='table-panier-moyen',
                    columns=[],
                    data=[],
                    sort_action='native',
                    style_table={'overflowX': 'auto'},
                    style_cell={
                        'textAlign': 'center',
                        'padding': '8px',
                        'fontFamily': 'Arial',
                        'fontSize': '14px',
                    },
                    style_header={
                        'backgroundColor': '#f8f9fa',
                        'fontWeight': 'bold',
                        'border': '1px solid #dee2e6',
                    },
                    style_data={'border': '1px solid #dee2e6'},
                ),
            ],
            style={'display': 'none'},
        ),
    ],
    fluid=True,
)


def calculer_variation(pays, annee_ref, n_ans, lookup):
    """Retourne la variation en % du panier moyen entre annee_ref et annee_ref - n_ans."""
    cle_actuelle = (pays, annee_ref)
    cle_precedente = (pays, annee_ref - n_ans)
    if cle_actuelle not in lookup or cle_precedente not in lookup:
        return None
    valeur_actuelle = lookup[cle_actuelle]
    valeur_precedente = lookup[cle_precedente]
    if valeur_precedente in (0, None) or pd.isna(valeur_precedente):
        return None
    return round((valeur_actuelle - valeur_precedente) / valeur_precedente * 100, 1)


# --- LOGIQUE INTERACTIVE (CALLBACK) ---
@callback(
    Output(component_id='graph-pays', component_property='figure'),
    Output(component_id='section-carte-vins', component_property='style'),
    Output(component_id='container-dropdown-annee', component_property='style'),
    Output(component_id='section-table-panier', component_property='style'),
    Output(component_id='table-panier-moyen', component_property='columns'),
    Output(component_id='table-panier-moyen', component_property='data'),
    Output(component_id='table-panier-moyen', component_property='style_data_conditional'),
    Input(component_id='radio-item-pays', component_property='value'),
    Input(component_id='dropdown-annee', component_property='value'),
)
def update_graph(graph_type, annee_selection):

    # Affiche la section texte + image seulement pour le premier bouton
    style_section = {'display': 'block'} if graph_type == 'geoclients' else {'display': 'none'}

    # Le menu déroulant Année n'a de sens que pour les boutons 1, 3 et 4
    style_dropdown = {'display': 'block'} if graph_type in boutons_avec_filtre_annee else {'display': 'none'}

    # Le tableau n'apparaît que pour le bouton 4
    style_table = {'display': 'block'} if graph_type == 'panierMoyen' else {'display': 'none'}

    # Valeurs par défaut du tableau (utilisées si on n'est pas sur "panierMoyen")
    table_columns, table_data, table_style_conditional = [], [], []

    # On filtre les données uniquement si on est sur un bouton concerné
    # et qu'une année précise (≠ "total") est sélectionnée
    if graph_type in boutons_avec_filtre_annee and annee_selection != 'total':
        df_filtre = df_intl[df_intl['annee'] == annee_selection]
        suffixe_titre = f" — Année {annee_selection}"
    else:
        df_filtre = df_intl
        suffixe_titre = ""

    if graph_type == 'geoclients':
        df_geo = (
            df_filtre.groupby(['PAYS_FACT', 'iso_alpha3'])
            .agg(nb_commandes=('Code_Client', 'count'), quantite_totale=('QUANTITE', 'sum'))
            .reset_index()
        )
        df_geo['quantite_log'] = np.log10(df_geo['quantite_totale'].clip(lower=1))

        fig = px.choropleth(
            df_geo,
            locations="iso_alpha3",
            color="quantite_log",
            color_continuous_scale="YlOrRd",
            hover_name="PAYS_FACT",
            hover_data={
                "nb_commandes": True,
                "quantite_totale": True,
                "quantite_log": False,
                "iso_alpha3": False,
            },
            projection="natural earth",
            title=f"Volume des commandes par pays de facturation{suffixe_titre}",
        )
        fig.update_geos(showcountries=True, countrycolor="LightGrey")
        fig.update_layout(
            margin={"r": 0, "t": 50, "l": 0, "b": 0},
            title_font_size=16,
            coloraxis_colorbar=dict(
                title="Quantité<br>commandée",
                tickvals=[0, 1, 2, 3, 4, 5],
                ticktext=["1", "10", "100", "1k", "10k", "100k"],
            ),
        )

    elif graph_type == 'evolutionPays':
        df_evo = (
            df_intl.groupby(['annee', 'PAYS_FACT'])['QUANTITE']
            .sum()
            .reset_index()
        )
        fig = px.area(
            df_evo,
            x='annee',
            y='QUANTITE',
            color='PAYS_FACT',
            groupnorm='percent',
            title="Évolution de la répartition des commandes par pays",
        )
        fig.update_layout(
            xaxis_title="Année",
            yaxis_title="Répartition des commandes par pays (%)",
            legend_title="Pays",
        )

        top5_pays = (
            df_intl.groupby('PAYS_FACT')['QUANTITE']
            .sum()
            .sort_values(ascending=False)
            .head(5)
            .index
            .tolist()
        )

        derniere_annee = df_evo['annee'].max()
        df_derniere = df_evo[df_evo['annee'] == derniere_annee].copy()
        df_derniere['pct'] = df_derniere['QUANTITE'] / df_derniere['QUANTITE'].sum() * 100

        ordre_pays = [trace.name for trace in fig.data]
        df_derniere['ordre'] = df_derniere['PAYS_FACT'].apply(
            lambda p: ordre_pays.index(p) if p in ordre_pays else -1
        )
        df_derniere = df_derniere.sort_values('ordre')
        df_derniere['cum_pct'] = df_derniere['pct'].cumsum()
        df_derniere['y_label'] = df_derniere['cum_pct'] - df_derniere['pct'] / 2

        for _, row in df_derniere[df_derniere['PAYS_FACT'].isin(top5_pays)].iterrows():
            fig.add_annotation(
                x=derniere_annee,
                y=row['y_label'],
                text=f"<b>{row['PAYS_FACT']}</b>",
                showarrow=False,
                xanchor='left',
                xshift=10,
                font=dict(size=11, color='black'),
            )

        fig.update_layout(margin=dict(r=120))

    elif graph_type == 'topPays':
        df_top = (
            df_filtre.groupby('PAYS_FACT')['QUANTITE']
            .sum()
            .reset_index(name='quantite_totale')
            .sort_values('quantite_totale', ascending=False)
            .head(15)
        )
        fig = px.bar(
            df_top,
            x='PAYS_FACT',
            y='quantite_totale',
            title=f"Top 15 des pays par quantité commandée{suffixe_titre}",
        )
        fig.update_layout(
            xaxis_title="Pays",
            yaxis_title="Quantité totale commandée",
        )

    elif graph_type == 'panierMoyen':

        # --- Carte : panier moyen par pays (pour l'année sélectionnée ou en moyenne globale) ---
        df_panier = (
            df_filtre.groupby(['PAYS_FACT', 'iso_alpha3'])
            .agg(quantite_totale=('QUANTITE', 'sum'), nb_commandes=('Code_Client', 'count'))
            .reset_index()
        )
        df_panier['panier_moyen'] = df_panier['quantite_totale'] / df_panier['nb_commandes']

        fig = px.choropleth(
            df_panier,
            locations="iso_alpha3",
            color="panier_moyen",
            color_continuous_scale="Blues",
            hover_name="PAYS_FACT",
            hover_data={
                "panier_moyen": ':.1f',
                "nb_commandes": True,
                "iso_alpha3": False,
            },
            projection="natural earth",
            title=f"Taille moyenne du panier par pays{suffixe_titre}",
        )
        fig.update_geos(showcountries=True, countrycolor="LightGrey")
        fig.update_layout(
            margin={"r": 0, "t": 50, "l": 0, "b": 0},
            title_font_size=16,
            coloraxis_colorbar=dict(title="Panier<br>moyen"),
        )

        # --- Tableau de classement ---
        annee_ref = annee_selection if annee_selection != 'total' else derniere_annee_globale

        # Table de correspondance (pays, année) -> panier_moyen, pour calculer les variations
        lookup_panier = df_yearly.set_index(['PAYS_FACT', 'annee'])['panier_moyen'].to_dict()

        # Données de l'année de référence pour panier moyen + fréquence
        df_ref = df_yearly[df_yearly['annee'] == annee_ref].copy()

        df_ref['var_1an'] = df_ref['PAYS_FACT'].apply(lambda p: calculer_variation(p, annee_ref, 1, lookup_panier))
        df_ref['var_2ans'] = df_ref['PAYS_FACT'].apply(lambda p: calculer_variation(p, annee_ref, 2, lookup_panier))
        df_ref['var_3ans'] = df_ref['PAYS_FACT'].apply(lambda p: calculer_variation(p, annee_ref, 3, lookup_panier))

        df_ref = df_ref.sort_values('panier_moyen', ascending=False)

        df_ref_affichage = df_ref.rename(columns={
            'PAYS_FACT': 'Pays',
            'panier_moyen': 'Panier moyen',
            'frequence': 'Fréquence (commandes/an)',
            'var_1an': 'Variation N-1 (%)',
            'var_2ans': 'Variation N-2 (%)',
            'var_3ans': 'Variation N-3 (%)',
        })[[
            'Pays', 'Panier moyen', 'Fréquence (commandes/an)',
            'Variation N-1 (%)', 'Variation N-2 (%)', 'Variation N-3 (%)',
        ]]

        df_ref_affichage['Panier moyen'] = df_ref_affichage['Panier moyen'].round(1)
        df_ref_affichage['Fréquence (commandes/an)'] = df_ref_affichage['Fréquence (commandes/an)'].astype(int)

        table_columns = [{'name': col, 'id': col} for col in df_ref_affichage.columns]
        table_data = df_ref_affichage.to_dict('records')

        # --- Coloration conditionnelle vert / rouge pour les colonnes de variation ---
        colonnes_variation = ['Variation N-1 (%)', 'Variation N-2 (%)', 'Variation N-3 (%)']
        table_style_conditional = []
        for col in colonnes_variation:
            table_style_conditional.append({
                'if': {'filter_query': f'{{{col}}} > 0', 'column_id': col},
                'color': 'green',
                'fontWeight': 'bold',
            })
            table_style_conditional.append({
                'if': {'filter_query': f'{{{col}}} < 0', 'column_id': col},
                'color': 'red',
                'fontWeight': 'bold',
            })

    return fig, style_section, style_dropdown, style_table, table_columns, table_data, table_style_conditional