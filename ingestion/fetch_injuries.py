# ingestion/fetch_injuries.py
# -----------------------------------------------------------------------------
# Ce script récupère la liste des joueurs blessés pour chaque ligue listée dans
# config/target_league_ids.yaml, pour la saison actuelle.
# -----------------------------------------------------------------------------

import os
import json
import yaml
from datetime import datetime
from utils.request_handler import get

# Détecter la saison actuelle (ex : 2023 pour 2023/24)
SEASON = datetime.now().year if datetime.now().month >= 7 else datetime.now().year - 1

# Charger les IDs de ligue
with open("config/target_league_ids.yaml", "r") as f:
    target_leagues = yaml.safe_load(f)["leagues"]

# Créer le dossier de sortie
os.makedirs("data/raw/injuries", exist_ok=True)

# Appels API
for league_id in target_leagues:
    params = {
        "league": league_id,
        "season": SEASON
    }
    try:
        response = get("/injuries", params=params)
        output_path = f"data/raw/injuries/injuries_{league_id}_{SEASON}.json"
        with open(output_path, "w") as f_out:
            json.dump(response, f_out, indent=2)
        print(f"✅ Données blessures enregistrées dans {output_path}")
    except Exception as e:
        print(f"❌ Erreur pour ligue {league_id} : {e}")
