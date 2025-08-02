# ingestion/fetch_pinnacle_odds.py
# -----------------------------------------------------------------------------
# Ce script récupère les cotes Pinnacle (1X2) uniquement pour les matchs du jour.
# Il filtre les marchés ouverts en Money Line (victoire, nul, défaite).
# -----------------------------------------------------------------------------

import os
import json
import yaml
import requests
from datetime import datetime

# Charger la clé API
with open("config/pinnacle_keys.yaml", "r") as f:
    keys = yaml.safe_load(f)

headers = {
    "x-rapidapi-key": keys["pinnacle"]["key"],
    "x-rapidapi-host": keys["pinnacle"]["host"]
}

# Requête vers les marchés de football
url = "https://pinnacle-odds.p.rapidapi.com/kit/v1/markets"
params = {"sport_id": 1}

try:
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    data = response.json()
except Exception as e:
    print(f"❌ Erreur lors de l'appel API Pinnacle: {e}")
    data = {}

# Date du jour (UTC)
TODAY = datetime.utcnow().date().isoformat()

# Filtrer les cotes du jour
odds = []
for ev in data.get("events", []):
    if not ev.get("is_have_odds"):
        continue
    if not ev["starts"].startswith(TODAY):
        continue
    try:
        ml = ev["periods"]["num_0"]["money_line"]
        odds.append({
            "event_id": ev["event_id"],
            "home": ev["home"],
            "away": ev["away"],
            "date": ev["starts"],
            "odds_home": ml["home"],
            "odds_draw": ml["draw"],
            "odds_away": ml["away"]
        })
    except KeyError:
        continue

# Sauvegarde
os.makedirs("data/raw/pinnacle", exist_ok=True)
with open("data/raw/pinnacle/odds_soccer.json", "w") as f_out:
    json.dump(odds, f_out, indent=2)

print("✅ Cotes Pinnacle du jour sauvegardées.")
