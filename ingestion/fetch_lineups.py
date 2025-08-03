# ingestion/fetch_lineups.py
# -----------------------------------------------------------------------------
# Ce script récupère les compositions d'équipe uniquement pour les matchs du jour,
# basés sur les ligues listées dans config/target_league_ids.yaml.
# -----------------------------------------------------------------------------

import os
import json
import yaml
from datetime import datetime

import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.request_handler import get

# Saison actuelle
SEASON = datetime.now().year if datetime.now().month >= 7 else datetime.now().year - 1
TODAY = datetime.now().date().isoformat()

# Charger les ligues cibles
with open("config/target_league_ids.yaml", "r") as f:
    leagues = yaml.safe_load(f)["leagues"]

# Répertoire de sortie
os.makedirs("data/raw/lineups", exist_ok=True)

# Parcourir les matchs du jour uniquement
for league_id in leagues:
    fixture_path = f"data/raw/fixtures_{league_id}_{SEASON}.json"
    if not os.path.exists(fixture_path):
        continue

    with open(fixture_path, "r") as f:
        fixtures = json.load(f)["response"]

    for match in fixtures:
        fixture = match["fixture"]
        if fixture["date"].startswith(TODAY):
            fixture_id = fixture["id"]
            try:
                lineups = get("/fixtures/lineups", params={"fixture": fixture_id})
                output_path = f"data/raw/lineups/lineups_{fixture_id}.json"
                with open(output_path, "w") as f_out:
                    json.dump(lineups, f_out, indent=2)
                print(f"✅ Lineup enregistré pour match {fixture_id}")
            except Exception as e:
                print(f"❌ Erreur pour match {fixture_id} : {e}") 
