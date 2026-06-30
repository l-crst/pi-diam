import pandas as pd

df = pd.read_csv('DataSet Mines(Feuil1).csv', sep=";")

df['Dat_Fact'] = pd.to_datetime(df['Dat_Fact'], format='%d/%m/%Y')
df['annee'] = df['Dat_Fact'].dt.year

commandes_par_an = df.groupby(['nom_client', 'annee']).size().reset_index(name='nb_commandes')

print(commandes_par_an)

classement = df.groupby('nom_client')['CA_EUR'].sum().reset_index()
classement.columns = ['nom_client', 'total_depense']
classement = classement.sort_values('total_depense', ascending=False)

print(classement)


bouchons_par_client = df.groupby('nom_client')['gamme'].unique().reset_index()
bouchons_par_client.columns = ['nom_client', 'gammes_bouchons']

print(bouchons_par_client)


clients_recents = df.groupby('nom_client')['Dat_Fact'].max().reset_index()
clients_recents = clients_recents.sort_values('Dat_Fact', ascending=False)

print(clients_recents)

from datetime import date

SEUIL_MOIS = 12
aujourd_hui = pd.Timestamp(date.today())

derniere_commande = df.groupby('nom_client')['Dat_Fact'].max().reset_index()
derniere_commande['jours_inactif'] = (aujourd_hui - derniere_commande['Dat_Fact']).dt.days
derniere_commande['churn'] = derniere_commande['jours_inactif'] > (SEUIL_MOIS * 30)

print(derniere_commande.sort_values('jours_inactif', ascending=False))


from datetime import date

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