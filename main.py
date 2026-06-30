import pandas as pd
import matplotlib.pyplot as plt
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

#5. Fréquence d'achat
df['Dat_Fact'] = pd.to_datetime(df['Dat_Fact'], errors='coerce')
df = df.dropna(subset=['nom_client', 'Dat_Fact'])
total_orders = df.groupby(['nom_client', 'Dat_Fact']).ngroups
unique_clients = df['nom_client'].nunique()
purchase_frequency = total_orders / unique_clients if unique_clients else 0.0

print({'total_orders': int(total_orders),'unique_clients': int(unique_clients),'purchase_frequency': purchase_frequency })

#6. Délai moyen entre 2 achats
    
df['Dat_Fact'] = pd.to_datetime(df['Dat_Fact'], errors='coerce')
df = df.dropna(subset=['nom_client', 'Dat_Fact'])
df = df.sort_values(['nom_client', 'Dat_Fact'])

interpurchase_days = (df.groupby('nom_client')['Dat_Fact'].diff().dt.days.dropna())
average_days = interpurchase_days.mean() if not interpurchase_days.empty else 0.0

print({'average_interpurchase_days': float(average_days),'num_intervals': int(len(interpurchase_days))})

# Graphique du nombre de clients en fonction du nombre de commandes
orders_per_client = df.groupby('nom_client').size()
clients_by_order_count = orders_per_client.value_counts().sort_index()

plt.figure(figsize=(12, 6))
plt.bar(clients_by_order_count.index, clients_by_order_count.values)
plt.title('Nombre de clients en fonction du nombre de commandes')
plt.xlabel('Nombre de commandes par client')
plt.ylabel('Nombre de clients')
plt.xlim(0, 150)
plt.grid(axis='y', linestyle='--', alpha=0.5)
plt.show()
