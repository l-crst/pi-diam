import pandas as pd
import matplotlib.pyplot as plt
from datetime import date
import matplotlib.pyplot as plt


df = pd.read_csv('DataSet Mines(Feuil1).csv', sep=";")

df['Dat_Fact'] = pd.to_datetime(df['Dat_Fact'], format='%d/%m/%Y')
df['annee'] = df['Dat_Fact'].dt.year
#transformer les , de la colonne CA_EUR en .  et supprimer les espaces pour pouvoir convertir en float
df['CA_EUR'] = df['CA_EUR'].str.replace(',', '.').str.replace(' ','').astype(float)


commandes_par_an = df.groupby(['nom_client', 'annee']).size().reset_index(name='nb_commandes')


classement = df.groupby('nom_client')['CA_EUR'].sum().reset_index()
classement.columns = ['nom_client', 'total_depense']
classement = classement.sort_values('total_depense', ascending=False)



bouchons_par_client = df.groupby('nom_client')['gamme'].unique().reset_index()
bouchons_par_client.columns = ['nom_client', 'gammes_bouchons']



clients_recents = df.groupby('nom_client')['Dat_Fact'].max().reset_index()
clients_recents = clients_recents.sort_values('Dat_Fact', ascending=False)


SEUIL_MOIS = 12
aujourd_hui = pd.Timestamp(date.today())

derniere_commande = df.groupby('nom_client')['Dat_Fact'].max().reset_index()
derniere_commande['jours_inactif'] = (aujourd_hui - derniere_commande['Dat_Fact']).dt.days
derniere_commande['churn'] = derniere_commande['jours_inactif'] > (SEUIL_MOIS * 30)






SEUIL_MOIS = 12
aujourd_hui = pd.Timestamp(date.today())

derniere_commande = df.groupby('nom_client')['Dat_Fact'].max().reset_index()
derniere_commande['jours_inactif'] = (aujourd_hui - derniere_commande['Dat_Fact']).dt.days
derniere_commande['churn'] = derniere_commande['jours_inactif'] > (SEUIL_MOIS * 30)

taux_churn = derniere_commande['churn'].mean() * 100




df['Dat_Fact'] = pd.to_datetime(df['Dat_Fact'], format='%d/%m/%Y')

# 2. Trouver la date de première commande pour chaque client
premiere_commande = df.groupby('nom_client')['Dat_Fact'].min()

# 3. Calculer la proportion de clients depuis plus de 3 ans
date_limite = pd.Timestamp.now() - pd.DateOffset(years=3)
proportion = (premiere_commande < date_limite).mean()



# === Taux de renouvellement des clients (année N -> année N+1) ===

# Ensemble des clients actifs par année
clients_par_annee = df.groupby('annee')['nom_client'].unique().apply(set)

annees = sorted(clients_par_annee.index)

resultats = []
for i in range(len(annees) - 1):
    annee_n = annees[i]
    annee_n1 = annees[i + 1]
    
    clients_n = clients_par_annee[annee_n]
    clients_n1 = clients_par_annee[annee_n1]
    
    clients_renouveles = clients_n & clients_n1  # clients présents les deux années
    
    nb_clients_n = len(clients_n)
    nb_renouveles = len(clients_renouveles)
    taux = (nb_renouveles / nb_clients_n * 100) if nb_clients_n > 0 else 0
    
    resultats.append({
        'annee_depart': annee_n,
        'annee_arrivee': annee_n1,
        'nb_clients_annee_depart': nb_clients_n,
        'nb_clients_renouveles': nb_renouveles,
        'taux_renouvellement_%': round(taux, 1)
    })

# === Analyse cross-selling : mono-gamme vs multi-gamme ===

# 1. Construction du tableau client : nb de gammes + dépense totale
analyse = (
    df.groupby('nom_client')
    .agg(nb_gammes=('gamme', 'nunique'), total_depense=('CA_EUR', 'sum'))
    .reset_index()
)

# 2. Classification mono / multi-gamme
analyse['type_client'] = analyse['nb_gammes'].apply(
    lambda x: 'Mono-gamme' if x == 1 else 'Multi-gamme'
)


# 3. Répartition en pourcentage des clients (mono vs multi)
nb_clients_total = analyse.shape[0]
repartition_clients = analyse['type_client'].value_counts(normalize=True).mul(100).round(1)


# 4. Statistiques de dépense par type de client
stats_par_type = analyse.groupby('type_client')['total_depense'].agg(
    nb_clients='count',
    depense_totale='sum',
    depense_moyenne='mean',
    depense_mediane='median'
).round(2)

stats_par_type['%_clients'] = (stats_par_type['nb_clients'] / nb_clients_total * 100).round(1)
stats_par_type['%_CA_total'] = (stats_par_type['depense_totale'] / stats_par_type['depense_totale'].sum() * 100).round(1)


# 5. Écart de dépense moyenne entre les deux groupes
depense_moy_mono = analyse.loc[analyse['type_client'] == 'Mono-gamme', 'total_depense'].mean()
depense_moy_multi = analyse.loc[analyse['type_client'] == 'Multi-gamme', 'total_depense'].mean()

# Fréquence d'achat moyenne par client (version explicite, 2+ commandes) 

# Nombre de commandes par client
nb_commandes = df.groupby('nom_client').size().reset_index(name='nb_commandes')

# Filtrer dès le départ les clients avec 2 commandes ou plus
clients_eligibles = nb_commandes[nb_commandes['nb_commandes'] >= 2]['nom_client']
df_filtre = df[df['nom_client'].isin(clients_eligibles)]



# Trier et calculer les écarts entre commandes consécutives
df_sorted = df_filtre.sort_values(['nom_client', 'Dat_Fact'])
df_sorted['jours_depuis_derniere_commande'] = (
    df_sorted.groupby('nom_client')['Dat_Fact'].diff().dt.days
)

# Fréquence moyenne par client
frequence_par_client = (
    df_sorted.groupby('nom_client')['jours_depuis_derniere_commande']
    .mean()
    .reset_index()
    .rename(columns={'jours_depuis_derniere_commande': 'frequence_moyenne_jours'})
    .merge(nb_commandes, on='nom_client')
    .sort_values('frequence_moyenne_jours')
)

frequence_par_client['commandes_par_an_estimees'] = (365 / frequence_par_client['frequence_moyenne_jours']).round(2)



frequence_globale = frequence_par_client['frequence_moyenne_jours'].mean()


# Délai moyen de réachat (un seul chiffre, clients 2+ commandes)

# 1. Garder uniquement les clients ayant 2 commandes ou plus
nb_commandes = df.groupby('nom_client').size()
clients_eligibles = nb_commandes[nb_commandes >= 2].index
df_filtre = df[df['nom_client'].isin(clients_eligibles)]

# 2. Trier par client puis par date
df_sorted = df_filtre.sort_values(['nom_client', 'Dat_Fact'])

# 3. Écart en jours entre chaque commande et la précédente, par client
df_sorted['delai_jours'] = df_sorted.groupby('nom_client')['Dat_Fact'].diff().dt.days

# 4. Délai moyen par client, puis moyenne globale de ces délais
delai_moyen_par_client = df_sorted.groupby('nom_client')['delai_jours'].mean()
delai_moyen_global = delai_moyen_par_client.mean()


#5. Fréquence d'achat
df['Dat_Fact'] = pd.to_datetime(df['Dat_Fact'], errors='coerce')
df = df.dropna(subset=['nom_client', 'Dat_Fact'])
total_orders = df.groupby(['nom_client', 'Dat_Fact']).ngroups
unique_clients = df['nom_client'].nunique()
purchase_frequency = total_orders / unique_clients if unique_clients else 0.0



#6. Délai moyen entre 2 achats
    
df['Dat_Fact'] = pd.to_datetime(df['Dat_Fact'], errors='coerce')
df = df.dropna(subset=['nom_client', 'Dat_Fact'])
df = df.sort_values(['nom_client', 'Dat_Fact'])

interpurchase_days = (df.groupby('nom_client')['Dat_Fact'].diff().dt.days.dropna())
average_days = interpurchase_days.mean() if not interpurchase_days.empty else 0.0


# Graphique du nombre de clients en fonction du nombre de commandes
orders_per_client = df.groupby('nom_client').size()
clients_by_order_count = orders_per_client.value_counts().sort_index()



# === Type de commande des nouveaux clients et évolution dans le temps ===

# 1. Trier les commandes par client et par date
df_sorted = df.sort_values(['nom_client', 'Dat_Fact']).copy()

# 2. Donner un numéro d'ordre à chaque commande, pour chaque client (1 = première commande, 2 = deuxième, etc.)
df_sorted['rang_commande'] = df_sorted.groupby('nom_client').cumcount() + 1

# 3. Répartition des gammes choisies lors de la 1ère commande (les "nouveaux clients")
premiere_commande = df_sorted[df_sorted['rang_commande'] == 1]

repartition_premiere_commande = (
    premiere_commande['gamme']
    .value_counts(normalize=True)
    .mul(100)
    .round(1)
)


# 4. Comparer avec la répartition des gammes sur les commandes suivantes (rang >= 2)
commandes_suivantes = df_sorted[df_sorted['rang_commande'] >= 2]

repartition_suivantes = (
    commandes_suivantes['gamme']
    .value_counts(normalize=True)
    .mul(100)
    .round(1)
)



# 5. Évolution détaillée : répartition des gammes pour chaque rang de commande (1ère, 2e, 3e, etc.)
evolution_par_rang = (
    df_sorted.groupby('rang_commande')['gamme']
    .value_counts(normalize=True)
    .mul(100)
    .round(1)
    .rename('pct')
    .reset_index()
)



# 6. Tableau croisé plus lisible : rang en ligne, gamme en colonne, % en valeur
tableau_evolution = (
    evolution_par_rang
    .pivot(index='rang_commande', columns='gamme', values='pct')
    .fillna(0)
)
rang_max = 10
tableau_graph = tableau_evolution.loc[tableau_evolution.index <= rang_max]




# === Évolution de la répartition du CA par gamme, selon le rang de commande ===

# 1. CA total généré par gamme, pour chaque rang de commande
evolution_ca_par_rang = (
    df_sorted.groupby(['rang_commande', 'gamme'])['CA_EUR']
    .sum()
    .reset_index()
)

# 2. Conversion en pourcentage : part de chaque gamme dans le CA total, pour chaque rang
evolution_ca_par_rang['pct_ca'] = (
    evolution_ca_par_rang
    .groupby('rang_commande')['CA_EUR']
    .transform(lambda x: x / x.sum() * 100)
    .round(1)
)


# 3. Tableau croisé : rang en ligne, gamme en colonne, % de CA en valeur
tableau_evolution_ca = (
    evolution_ca_par_rang
    .pivot(index='rang_commande', columns='gamme', values='pct_ca')
    .fillna(0)
)
tableau_graph_ca = tableau_evolution_ca.loc[tableau_evolution_ca.index <= rang_max]

#Panier moyen 
def calculer_paniers(df: pd.DataFrame) -> pd.DataFrame:
    """Regroupe les commandes par client et par jour pour former des paniers."""
    return (
        df.groupby(['nom_client', 'Dat_Fact'])
        .agg(montant_panier=('CA_EUR', 'sum'), nb_lignes=('CA_EUR', 'size'))
        .reset_index()
    )


def calculer_panier_moyen_par_client(paniers: pd.DataFrame) -> pd.DataFrame:
    return (
        paniers.groupby('nom_client')['montant_panier']
        .mean()
        .reset_index(name='panier_moyen')
        .sort_values('panier_moyen', ascending=False)
    )


def calculer_evolution_panier_moyen(paniers: pd.DataFrame) -> pd.DataFrame:
    paniers = paniers.copy()
    paniers['mois'] = paniers['Dat_Fact'].dt.to_period('M')
    return (
        paniers.groupby('mois')['montant_panier']
        .mean()
        .reset_index(name='panier_moyen')
    )
paniers = calculer_paniers(df)
evolution_panier_moyen = calculer_evolution_panier_moyen(paniers)


def tracer_evolution_panier_moyen(evolution_panier_moyen: pd.DataFrame, nom_fichier: str) -> None:
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(
        evolution_panier_moyen['mois'].astype(str),
        evolution_panier_moyen['panier_moyen'],
        marker='o'
    )
    ax.set_xlabel("Mois")
    ax.set_ylabel("Panier moyen (EUR)")
    ax.set_title("Évolution du panier moyen dans le temps")
    ax.tick_params(axis='x', rotation=90)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(nom_fichier, dpi=150)
    plt.close(fig)

if __name__ == "__main__":
    print("Nombre de commandes par client et par année :")
    print(commandes_par_an)

    print("Classement des clients par dépense totale :")
    print(classement)

    print("Gammes de bouchons par client :")
    print(bouchons_par_client)

    print("Clients les plus récents :")
    print(clients_recents)

    print("Dernière commande et jours d'inactivité par client :")
    print(derniere_commande.sort_values('jours_inactif', ascending=False))

    print(derniere_commande)
    print(f"\nTaux de churn : {taux_churn:.1f}%")

    print(f"Proportion de clients depuis plus de 3 ans : {proportion:.2%}")


    print("Détail par client :")
    print(analyse.sort_values('total_depense', ascending=False))

    print(f"\nNombre total de clients : {nb_clients_total}")
    for type_client in ['Mono-gamme', 'Multi-gamme']:
        nb = (analyse['type_client'] == type_client).sum()
        pct = repartition_clients.get(type_client, 0)
        print(f"{type_client} : {nb} clients ({pct}%)")

    print(f"Clients exclus (1 seule commande) : {df['nom_client'].nunique() - clients_eligibles.shape[0]}")
    print(f"Clients conservés (2+ commandes) : {clients_eligibles.shape[0]}")

    print("\nRépartition détaillée du nombre de gammes achetées :")
    print(analyse['nb_gammes'].value_counts().sort_index())

    print("\nStatistiques par type de client :")
    print(stats_par_type)

    print("\nFréquence d'achat moyenne par client :")
    print(frequence_par_client)

    print(f"\nFréquence d'achat moyenne globale : {frequence_globale:.1f} jours entre deux commandes")

    print(f"En moyenne, un client recommande au bout de {delai_moyen_global:.0f} jours.")

    print({'total_orders': int(total_orders),'unique_clients': int(unique_clients),'purchase_frequency': purchase_frequency })

    print({'average_interpurchase_days': float(average_days), 'num_intervals': int(len(interpurchase_days))})

    for type_client in ['Mono-gamme', 'Multi-gamme']:
        nb = (analyse['type_client'] == type_client).sum()
        pct = repartition_clients.get(type_client, 0)
        print(f"{type_client} : {nb} clients ({pct}%)")

    if pd.notna(depense_moy_mono) and depense_moy_mono > 0:
        ecart = (depense_moy_multi - depense_moy_mono) / depense_moy_mono * 100
        print(f"\nLes clients multi-gamme dépensent en moyenne {ecart:.1f}% de plus que les clients mono-gamme.")

    plt.figure(figsize=(12, 6))
    plt.bar(clients_by_order_count.index, clients_by_order_count.values)
    plt.title('Nombre de clients en fonction du nombre de commandes')
    plt.xlabel('Nombre de commandes par client')
    plt.ylabel('Nombre de clients')
    plt.xlim(0, 150)
    plt.grid(axis='y', linestyle='--', alpha=0.5)
    plt.show()

    print("Répartition des gammes choisies à la 1ère commande (nouveaux clients) :")
    print(repartition_premiere_commande)

    print("\nRépartition des gammes sur les commandes suivantes (clients fidélisés) :")
    print(repartition_suivantes)

    print("\nÉvolution de la répartition des gammes selon le rang de commande :")
    print(evolution_par_rang)

    print("\nTableau croisé (rang de commande x gamme, en %) :")
    print(tableau_evolution)

    # === Graphique : évolution de la répartition des gammes selon le rang de commande ===

    # On limite aux premiers rangs pour rester lisible (les rangs très élevés ont peu de clients)
    rang_max = 10
    tableau_graph = tableau_evolution.loc[tableau_evolution.index <= rang_max]

    fig, ax = plt.subplots(figsize=(10, 6))

    ax.stackplot(
        tableau_graph.index,
        [tableau_graph[col] for col in tableau_graph.columns],
        labels=tableau_graph.columns,
        alpha=0.85
    )

    ax.set_xlabel("Rang de la commande (1 = première commande)")
    ax.set_ylabel("Répartition des gammes (%)")
    ax.set_title("Évolution de la répartition des gammes selon l'ancienneté du client")
    ax.legend(title="Gamme", loc='upper left', bbox_to_anchor=(1.02, 1))
    ax.set_xlim(tableau_graph.index.min(), tableau_graph.index.max())
    ax.set_ylim(0, 100)

    plt.tight_layout()
    plt.savefig('evolution_gammes.png', dpi=150)
    plt.show()

    print("Évolution de la répartition du CA par gamme selon le rang de commande :")
    print(evolution_ca_par_rang)

    print("\nTableau croisé CA (rang de commande x gamme, en %) :")
    print(tableau_evolution_ca)

    # 4. Graphique en courbes empilées (même format que le graphique précédent)
    rang_max = 10
    tableau_graph_ca = tableau_evolution_ca.loc[tableau_evolution_ca.index <= rang_max]

    fig, ax = plt.subplots(figsize=(10, 6))

    ax.stackplot(
        tableau_graph_ca.index,
        [tableau_graph_ca[col] for col in tableau_graph_ca.columns],
        labels=tableau_graph_ca.columns,
        alpha=0.85
    )

    ax.set_xlabel("Rang de la commande (1 = première commande)")
    ax.set_ylabel("Répartition du chiffre d'affaires par gamme (%)")
    ax.set_title("Évolution de la répartition du CA par gamme selon l'ancienneté du client")
    ax.legend(title="Gamme", loc='upper left', bbox_to_anchor=(1.02, 1))
    ax.set_xlim(tableau_graph_ca.index.min(), tableau_graph_ca.index.max())
    ax.set_ylim(0, 100)

    plt.tight_layout()
    plt.savefig('evolution_gammes_ca.png', dpi=150)
    plt.show()

    paniers = calculer_paniers(df)
    print("Détail des paniers (client x jour) :")
    print(paniers)

    panier_moyen_global = paniers['montant_panier'].mean()
    print(f"\nPanier moyen global : {panier_moyen_global:.2f} EUR")

    panier_moyen_par_client = calculer_panier_moyen_par_client(paniers)
    print("\nPanier moyen par client :")
    print(panier_moyen_par_client)

    evolution_panier_moyen = calculer_evolution_panier_moyen(paniers)
    print("\nÉvolution du panier moyen par mois :")
    print(evolution_panier_moyen)

    tracer_evolution_panier_moyen(evolution_panier_moyen, 'evolution_panier_moyen.png')
    print("\nGraphique enregistré : evolution_panier_moyen.png")

