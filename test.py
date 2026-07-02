import plotly.express as px
from main import *

couleurs = {
    "Champions (à chouchouter)":          "#2ecc71",
    "Gros clients perdus (à réactiver)":  "#e74c3c",
    "Petits clients actifs (à développer)":"#3498db",
    "Petits clients inactifs (à surveiller)":"#95a5a6"
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
fig.add_hline(y=seuil_ca,      line_dash="dash", line_color="grey", line_width=1)


max_ca = client_df["total_ca"].max()

fig.add_annotation(x=50,  y=max_ca * 0.9, text="<b>CHAMPIONS<br>à chouchouter</b>", font=dict(color="#2ecc71", size=12), showarrow=False)
fig.add_annotation(x=400, y=max_ca * 0.9, text="<b>GROS CLIENTS PERDUS<br>à réactiver d'urgence</b>", font=dict(color="#e74c3c", size=12), showarrow=False)
fig.add_annotation(x=50,  y=seuil_ca * 0.1, text="Petits clients<br>actifs", font=dict(color="#3498db", size=10), showarrow=False)
fig.add_annotation(x=400, y=seuil_ca * 0.1, text="Petits clients<br>inactifs", font=dict(color="#95a5a6", size=10), showarrow=False)

# 5. Formatage final (axes, dimensions, thème)
fig.update_layout(
    yaxis=dict(tickformat="s", ticksuffix="€"),  # Transforme automatiquement "1000" en "1k€"
    template="plotly_white",                     # Thème épuré proche de Matplotlib
    width=1000,
    height=650,
    legend_title_text="",                        # Enlève le titre "segment" au-dessus de la légende pour faire plus propre
    legend=dict(yanchor="top", y=0.99, xanchor="right", x=0.99) # Positionnement de la légende
)

# Affichage interactif
fig.show()