# ingestion/fetch_odds_api_football.py
import os
import json
import yaml
from datetime import datetime
import sys

# Ajout du chemin pour import utils
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.request_handler import get

# Dossier de sortie
os.makedirs("data/raw/api_football_odds", exist_ok=True)

# Charger les fixtures du jour (à partir des fichiers fixtures_<league_id>_<date>.json)
today = datetime.now().strftime("%Y-%m-%d")
with open("config/target_league_ids.yaml") as f:
    leagues = yaml.safe_load(f).get("leagues", [])

for league_id in leagues:
    fixtures_file = f"data/raw/fixtures_{league_id}_{today}.json"
    if not os.path.exists(fixtures_file):
        continue

    with open(fixtures_file) as f_fix:
        fixtures = json.load(f_fix).get("response", [])

    for match in fixtures:
        fixture_id = match["fixture"]["id"]
        try:
            # Appel de l’endpoint odds/fixture pour récupérer les cotes du match
            odds_resp = get(f"/odds/fixture/{fixture_id}")
            # Vous devrez explorer la structure retournée pour extraire les cotes 1X2
            # par exemple bookmaker->bets->values avec "Home", "Draw", "Away".
            out = f"data/raw/api_football_odds/odds_{fixture_id}.json"
            with open(out, "w") as f_out:
                json.dump(odds_resp, f_out, indent=2)
            print(f"✅ Cotes sauvegardées pour le match {fixture_id}")
        except Exception as e:
            print(f"❌ Erreur lors de la récupération des cotes pour {fixture_id} : {e}")
