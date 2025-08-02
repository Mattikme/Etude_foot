# ingestion/fetch_stats.py
# -----------------------------------------------------------------------------
# Ce script récupère les statistiques détaillées pour les matchs du jour
# uniquement (toutes ligues de target_league_ids.yaml).
# Cela permet de limiter la consommation d'API.
# -----------------------------------------------------------------------------

import os
import json
import yaml
from datetime import datetime
from utils.request_handler import get

SEASON = datetime.now().year if datetime.now().month >= 7 else datetime.now().year - 1
TODAY = datetime.now().date()

with open("config/target_league_ids.yaml", "r") as f:
    target_leagues = yaml.safe_load(f)["leagues"]

os.makedirs("data/raw/stats", exist_ok=True)

for league_id in target_leagues:
    fixtures_path = f"data/raw/fixtures_{league_id}_{SEASON}.json"
    if not os.path.exists(fixtures_path):
        print(f"⚠️ Fixtures manquants pour ligue {league_id}, ignoré.")
        continue

    with open(fixtures_path, "r") as f:
        fixtures = json.load(f)

    for match in fixtures["response"]:
        fixture = match["fixture"]
        fixture_date = datetime.fromisoformat(fixture["date"]).date()

        if fixture_date != TODAY:
            continue

        fixture_id = fixture["id"]
        try:
            stats = get("/fixtures/statistics", params={"fixture": fixture_id})
            output_path = f"data/raw/stats/statistics_{fixture_id}.json"
            with open(output_path, "w") as f_out:
                json.dump(stats, f_out, indent=2)
            print(f"✅ Statistiques enregistrées pour match {fixture_id}")
        except Exception as e:
            print(f"❌ Erreur pour fixture {fixture_id} : {e}") 
