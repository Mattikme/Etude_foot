# ingestion/fetch_odds_api_football.py
import os
import json
import yaml
import sys
import time
from datetime import datetime

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.request_handler import get

today = datetime.now().strftime("%Y-%m-%d")
BOOKMAKER_ID = 8  # Remplacez par 34 pour "Superbet" ou toute autre valeur souhaitée

with open("config/target_league_ids.yaml") as f:
    cfg = yaml.safe_load(f)
    leagues = cfg.get("leagues", cfg)
    if isinstance(leagues, dict):
        target_leagues = [int(v) for v in leagues.values()]
    else:
        target_leagues = [int(x) for x in leagues]

os.makedirs("data/raw/api_football_odds", exist_ok=True)

for league_id in target_leagues:
    try:
        odds_resp = get("/odds", params={
            "league": league_id,
            "date": today,
            "bookmaker": BOOKMAKER_ID
        })
    except Exception as e:
        print(f"❌ Erreur lors de la récupération des cotes pour la ligue {league_id} : {e}")
        time.sleep(1)
        continue

    matches = odds_resp.get("response", [])
    if not matches:
        print(f"⚠️ Aucune cote disponible aujourd'hui pour la ligue {league_id}")
        time.sleep(1)
        continue

    saved = 0
    for match in matches:
        fixture_id = match.get("fixture", {}).get("id")
        if fixture_id is None:
            continue
        out_path = f"data/raw/api_football_odds/odds_{fixture_id}.json"
        with open(out_path, "w") as out_file:
            json.dump(match, out_file, indent=2)
        saved += 1

    print(f"✅ {saved} fichier(s) de cotes enregistré(s) pour la ligue {league_id}")
    # Petite pause pour éviter un dépassement de quota
    time.sleep(1)
 
