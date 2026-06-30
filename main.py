import pandas as pd
from datetime import date


df = pd.read_csv('DataSet Mines(Feuil1).csv', sep=";")

df['Dat_Fact'] = pd.to_datetime(df['Dat_Fact'], format='%d/%m/%Y')
df['annee'] = df['Dat_Fact'].dt.year
#transformer les , de la colonne CA_EUR en .  et supprimer les espaces pour pouvoir convertir en float
df['CA_EUR'] = df['CA_EUR'].str.replace(',', '.').str.replace(' ','').astype(float)


commandes_par_an = df.groupby(['nom_client', 'annee']).size().reset_index(name='nb_commandes')
print("Nombre de commandes par client et par année :")
print(commandes_par_an)

classement = df.groupby('nom_client')['CA_EUR'].sum().reset_index()
classement.columns = ['nom_client', 'total_depense']
classement = classement.sort_values('total_depense', ascending=False)
print("Classement des clients par dépense totale :")
print(classement)


bouchons_par_client = df.groupby('nom_client')['gamme'].unique().reset_index()
bouchons_par_client.columns = ['nom_client', 'gammes_bouchons']
print("Gammes de bouchons par client :")
print(bouchons_par_client)


clients_recents = df.groupby('nom_client')['Dat_Fact'].max().reset_index()
clients_recents = clients_recents.sort_values('Dat_Fact', ascending=False)
print("Clients les plus récents :")
print(clients_recents)


SEUIL_MOIS = 12
aujourd_hui = pd.Timestamp(date.today())

derniere_commande = df.groupby('nom_client')['Dat_Fact'].max().reset_index()
derniere_commande['jours_inactif'] = (aujourd_hui - derniere_commande['Dat_Fact']).dt.days
derniere_commande['churn'] = derniere_commande['jours_inactif'] > (SEUIL_MOIS * 30)

print("Dernière commande et jours d'inactivité par client :")
print(derniere_commande.sort_values('jours_inactif', ascending=False))




SEUIL_MOIS = 12
aujourd_hui = pd.Timestamp(date.today())

derniere_commande = df.groupby('nom_client')['Dat_Fact'].max().reset_index()
derniere_commande['jours_inactif'] = (aujourd_hui - derniere_commande['Dat_Fact']).dt.days
derniere_commande['churn'] = derniere_commande['jours_inactif'] > (SEUIL_MOIS * 30)

taux_churn = derniere_commande['churn'].mean() * 100

print(derniere_commande)
print(f"\nTaux de churn : {taux_churn:.1f}%")



df['Dat_Fact'] = pd.to_datetime(df['Dat_Fact'], format='%d/%m/%Y')

# 2. Trouver la date de première commande pour chaque client
premiere_commande = df.groupby('nom_client')['Dat_Fact'].min()

# 3. Calculer la proportion de clients depuis plus de 3 ans
date_limite = pd.Timestamp.now() - pd.DateOffset(years=3)
proportion = (premiere_commande < date_limite).mean()

print(f"Proportion de clients depuis plus de 3 ans : {proportion:.2%}")

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

renouvellement_df = pd.DataFrame(resultats)
print("Taux de renouvellement année par année :")
print(renouvellement_df)
taux_moyen = renouvellement_df['taux_renouvellement_%'].mean()
print(f"\nTaux de renouvellement moyen : {taux_moyen:.1f}%")

#Analyse cross-selling : mono-gamme vs multi-gamme

# Construction du tableau client : nb de gammes + dépense totale
analyse = (
    df.groupby('nom_client')
    .agg(nb_gammes=('gamme', 'nunique'), total_depense=('CA_EUR', 'sum'))
    .reset_index()
)

# Classification mono / multi-gamme
analyse['type_client'] = analyse['nb_gammes'].apply(
    lambda x: 'Mono-gamme' if x == 1 else 'Multi-gamme'
)

print("Détail par client :")
print(analyse.sort_values('total_depense', ascending=False))

# Répartition en pourcentage des clients (mono vs multi)
nb_clients_total = analyse.shape[0]
repartition_clients = analyse['type_client'].value_counts(normalize=True).mul(100).round(1)

print(f"\nNombre total de clients : {nb_clients_total}")
for type_client in ['Mono-gamme', 'Multi-gamme']:
    nb = (analyse['type_client'] == type_client).sum()
    pct = repartition_clients.get(type_client, 0)
    print(f"{type_client} : {nb} clients ({pct}%)")

print("\nRépartition détaillée du nombre de gammes achetées :")
print(analyse['nb_gammes'].value_counts().sort_index())

# Statistiques de dépense par type de client
stats_par_type = analyse.groupby('type_client')['total_depense'].agg(
    nb_clients='count',
    depense_totale='sum',
    depense_moyenne='mean',
    depense_mediane='median'
).round(2)

stats_par_type['%_clients'] = (stats_par_type['nb_clients'] / nb_clients_total * 100).round(1)
stats_par_type['%_CA_total'] = (stats_par_type['depense_totale'] / stats_par_type['depense_totale'].sum() * 100).round(1)

print("\nStatistiques par type de client :")
print(stats_par_type)

# Écart de dépense moyenne entre les deux groupes
depense_moy_mono = analyse.loc[analyse['type_client'] == 'Mono-gamme', 'total_depense'].mean()
depense_moy_multi = analyse.loc[analyse['type_client'] == 'Multi-gamme', 'total_depense'].mean()

if pd.notna(depense_moy_mono) and depense_moy_mono > 0:
    ecart = (depense_moy_multi - depense_moy_mono) / depense_moy_mono * 100
    print(f"\nLes clients multi-gamme dépensent en moyenne {ecart:.1f}% de plus que les clients mono-gamme.")

# Fréquence d'achat moyenne par client (version explicite, 2+ commandes) 

# Nombre de commandes par client
nb_commandes = df.groupby('nom_client').size().reset_index(name='nb_commandes')

# Filtrer dès le départ les clients avec 2 commandes ou plus
clients_eligibles = nb_commandes[nb_commandes['nb_commandes'] >= 2]['nom_client']
df_filtre = df[df['nom_client'].isin(clients_eligibles)]

print(f"Clients exclus (1 seule commande) : {df['nom_client'].nunique() - clients_eligibles.shape[0]}")
print(f"Clients conservés (2+ commandes) : {clients_eligibles.shape[0]}")

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

print("\nFréquence d'achat moyenne par client :")
print(frequence_par_client)

frequence_globale = frequence_par_client['frequence_moyenne_jours'].mean()
print(f"\nFréquence d'achat moyenne globale : {frequence_globale:.1f} jours entre deux commandes")

# === Délai moyen de réachat (un seul chiffre, clients 2+ commandes) ===

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

print(f"En moyenne, un client recommande au bout de {delai_moyen_global:.0f} jours.")