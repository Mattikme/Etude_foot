# ingestion/fetch_standings.py
# -----------------------------------------------------------------------------
# Ce script récupère le classement complet d'une ligue pour une saison donnée
# via l'endpoint /standings. Il peut être utilisé pour créer des features
# comme la position actuelle ou l'écart de points entre équipes.
# -----------------------------------------------------------------------------

import os
import json
from utils.request_handler import get

LEAGUE_ID = 39
SEASON = 2022

params = {
    "league": LEAGUE_ID,
    "season": SEASON
}

response = get("/standings", params=params)

# Répertoire de sortie
os.makedirs("data/raw/standings", exist_ok=True)

# Sauvegarde du JSON
output_path = f"data/raw/standings/standings_{LEAGUE_ID}_{SEASON}.json"
with open(output_path, "w") as f:
    json.dump(response, f, indent=2)

print(f"✅ Classement sauvegardé dans {output_path}")
