# ingestion/fetch_injuries.py
# -----------------------------------------------------------------------------
# Ce script permet de récupérer la liste des joueurs blessés pour une ligue
# donnée via l'endpoint /injuries de l'API-Football.
# Utile pour ajuster les features ou détecter des absences clés.
# -----------------------------------------------------------------------------

import os
import json
from utils.request_handler import get

LEAGUE_ID = 39
SEASON = 2022

# Appel direct à l'endpoint injuries (pas besoin de passer par les fixtures)
params = {
    "league": LEAGUE_ID,
    "season": SEASON
}
response = get("/injuries", params=params)

# Répertoire de sortie
os.makedirs("data/raw/injuries", exist_ok=True)

# Sauvegarde du JSON
output_path = f"data/raw/injuries/injuries_{LEAGUE_ID}_{SEASON}.json"
with open(output_path, "w") as f:
    json.dump(response, f, indent=2)

print(f"✅ Données blessures enregistrées dans {output_path}")
