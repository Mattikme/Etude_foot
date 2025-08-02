# ingestion/fetch_fixtures.py
# -----------------------------------------------------------------------------
# Ce script permet de récupérer tous les matchs d'une saison en cours pour toutes
# les ligues listées dans target_league_ids.yaml via l'API-Football.
# -----------------------------------------------------------------------------

import os
import json
import yaml
from datetime import datetime
from utils.request_handler import get

# Détecter la saison actuelle (ex : saison 2023-2024 = 2023)
SEASON = datetime.now().year if datetime.now().month >= 7 else datetime.now().year - 1

# Charger les IDs de ligue depuis le YAML
with open("config/target_league_ids.yaml", "r") as f:
    target_leagues = yaml.safe_load(f)["leagues"]

# Créer le dossier de sortie
os.makedirs("data/raw", exist_ok=True)

# Requête pour chaque ligue
for league_id in target_leagues:
    params = {
        "league": league_id,
        "season": SEASON
    }
    try:
        response = get("/fixtures", params=params)
        output_path = f"data/raw/fixtures_{league_id}_{SEASON}.json"
        with open(output_path, "w") as f_out:
            json.dump(response, f_out, indent=2)
        print(f"✅ Fixtures sauvegardés dans {output_path}")
    except Exception as e:
        print(f"❌ Erreur lors de la récupération des fixtures pour ligue {league_id} : {e}")
