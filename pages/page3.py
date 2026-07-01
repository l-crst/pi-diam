# pour la nouvelle data a l'international

import dash
from main import *
from dash import html, dcc, callback, Input, Output
import plotly.express as px
import dash_bootstrap_components as dbc
import pandas as pd
import numpy as np
import pycountry

dash.register_page(__name__)

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
    # Si virgule présente = séparateur décimal français
    # -> on retire les points (milliers) puis on remplace la virgule par un point
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
    # Corrections pour codes d'usage non-ISO standard
    corrections = {"UK": "GB", "EL": "GR"}
    code = corrections.get(code, code)
    try:
        pays = pycountry.countries.get(alpha_2=code)
        return pays.alpha_3 if pays else None
    except Exception:
        return None


df_intl['iso_alpha3'] = df_intl['PAYS_FACT'].apply(convertir_iso2_en_iso3)

# --- OPTIONS DU RADIO ---
options = [
    {'label': 'Répartition géographique des clients', 'value': 'geoclients'},
    {'label': 'Évolution des commandes par pays', 'value': 'evolutionPays'},
    {'label': 'Top pays par quantité', 'value': 'topPays'},
]

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
    ],
    fluid=True,
)


# --- LOGIQUE INTERACTIVE (CALLBACK) ---
@callback(
    Output(component_id='graph-pays', component_property='figure'),
    Input(component_id='radio-item-pays', component_property='value')
)
def update_graph(graph_type):

    if graph_type == 'geoclients':
        df_geo = (
            df_intl.groupby(['PAYS_FACT', 'iso_alpha3'])
            .agg(nb_commandes=('Code_Client', 'count'), quantite_totale=('QUANTITE', 'sum'))
            .reset_index()
        )
        # Échelle logarithmique pour éviter que la France (ou tout autre
        # gros marché) n'écrase visuellement les autres pays
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
            title="Volume des commandes par pays de facturation",
        )
        fig.update_geos(
            showcountries=True,
            countrycolor="LightGrey",
        )
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

    elif graph_type == 'topPays':
        df_top = (
            df_intl.groupby('PAYS_FACT')['QUANTITE']
            .sum()
            .reset_index(name='quantite_totale')
            .sort_values('quantite_totale', ascending=False)
            .head(15)
        )
        fig = px.bar(
            df_top,
            x='PAYS_FACT',
            y='quantite_totale',
            title="Top 15 des pays par quantité commandée",
        )
        fig.update_layout(
            xaxis_title="Pays",
            yaxis_title="Quantité totale commandée",
        )

    return fig