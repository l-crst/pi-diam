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
            options=['dépenseClient', 'nbCommandesClient','commandesAn',"Ancienneté des clients"],
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
    elif graph_type == "Ancienneté des clients":
        df_pie = repartition.reset_index()
        df_pie.columns = ["Anciennete", "Valeur"]
        fig = px.pie(
            df_pie,
            names="Anciennete",
            values="Valeur",
            title="Répartition de l'ancienneté des clients",
            color_discrete_sequence=["#ff9999", "#66b3ff", "#99ff99", "#ffcc99"],
        )
        fig.update_traces(textinfo="percent+label")
    return fig

# Run the app
if __name__ == '__main__':
    app.run(debug=True)