# ingestion/fetch_fixtures.py
# -----------------------------------------------------------------------------
# Ce script permet de récupérer tous les matchs d'une ligue et saison spécifique
# (ex : Premier League 2022/2023) depuis l'API-Football, et de les sauvegarder.
# -----------------------------------------------------------------------------

import os
import json
from utils.request_handler import get

# Exemple : Premier League (league_id=39), saison 2022
LEAGUE_ID = 39
SEASON = 2022

# Requête à l'API pour les fixtures de la ligue et saison donnée
params = {
    "league": LEAGUE_ID,
    "season": SEASON
}
response = get("/fixtures", params=params)

# Créer le dossier de sortie si nécessaire
os.makedirs("data/raw", exist_ok=True)

# Enregistrer la réponse JSON brute
output_path = f"data/raw/fixtures_{LEAGUE_ID}_{SEASON}.json"
with open(output_path, "w") as f:
    json.dump(response, f, indent=2)

print(f"✅ Fixtures sauvegardés dans {output_path}")
 
