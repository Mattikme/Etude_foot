# ingestion/fetch_lineups.py
# -----------------------------------------------------------------------------
# Ce script permet de récupérer les compositions d'équipe (lineups) pour
# tous les matchs des ligues listées dans config/target_league_ids.yaml.
# -----------------------------------------------------------------------------

import os
import json
import yaml
from datetime import datetime
from utils.request_handler import get

# Saison dynamique : commence en juillet
SEASON = datetime.now().year if datetime.now().month >= 7 else datetime.now().year - 1

# Charger les ligues cibles
with open("config/target_league_ids.yaml", "r") as f:
    target_leagues = yaml.safe_load(f)["leagues"]

# Répertoire de sortie
os.makedirs("data/raw/lineups", exist_ok=True)

# Parcourir les fixtures de chaque ligue
for league_id in target_leagues:
    fixtures_path = f"data/raw/fixtures_{league_id}_{SEASON}.json"

    if not os.path.exists(fixtures_path):
        print(f"⚠️ Pas de fixtures pour ligue {league_id}, ignoré.")
        continue

    with open(fixtures_path, "r") as f:
        fixtures = json.load(f)

    fixture_ids = [match["fixture"]["id"] for match in fixtures["response"]]

    for fixture_id in fixture_ids:
        try:
            lineups = get("/fixtures/lineups", params={"fixture": fixture_id})
            output_path = f"data/raw/lineups/lineups_{fixture_id}.json"
            with open(output_path, "w") as f_out:
                json.dump(lineups, f_out, indent=2)
            print(f"✅ Lineup enregistré pour match {fixture_id}")
        except Exception as e:
            print(f"❌ Erreur pour fixture {fixture_id} : {e}")
