# INSEE API Sirene v3 Client (Python)
Ce projet propose un client Python pour interroger l’API Sirene de l’INSEE
via des requêtes unitaires et multi-critères, avec gestion :

- des filtres complexes (`q`)
- de la pagination par curseur
- des erreurs API (401, 404, 429)
- de la transformation des résultats en DataFrame pandas

# Usecases:
- Extraction massive d’établissements (SIRET) ou d’unités légales (SIREN)
- Analyses sectorielles (NAF, périodes, dates de traitement)
- Intégration dans un pipeline data ou un notebook d’analyse

# Stack technique:
- Python 3.10+
- requests
- pandas
- python-dotenv

# Installation:
git clone https://github.com/TON_USER/insee-api-sirene-v3-client.git

cd insee-api-sirene-v3-client

pip install -r requirements.txt

# Configuration:
Créer un fichier `.env` à la racine du projet :

INSEE_API_KEY=xxxxxxxxxxxxxxxx

# Exemple d'utilisation:
from src.insee-api-siene-v3-client import requete_multi_criteres

df = requete_multi_criteres(
    endpoint="siret",
    q='periode(activitePrincipaleEtablissement:70.10Z)',
    max_rows=1500
)

print(df.shape)

# Fonctionnalités clé:
✔ Requêtes unitaires (SIREN / SIRET)  
✔ Requêtes multi-critères (`q` libre avec AND / OR / parenthèses)  
✔ Normalisation des dates dans les requêtes  
✔ Pagination par curseur
✔ Gestion des erreurs HTTP (401, 404, 429)  
✔ Résultats exploitables en pandas DataFrame  

# Démo:
Un notebook de démonstration est disponible dans le dossier `notebooks/`
pour illustrer les requêtes et l’analyse des résultats.

# Points techniques:
- Séparation claire entre logique métier et démonstration
- Gestion propre des secrets (pas de clé en dur)
- Code réutilisable et testable
- Compatible avec un usage CI/CD

