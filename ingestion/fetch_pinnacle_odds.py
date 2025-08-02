# ingestion/fetch_pinnacle_odds.py
# -----------------------------------------------------------------------------
# Ce script récupère les cotes Pinnacle pré-match pour le football (sport_id = 1).
# Il extrait les cotes 1X2 (Money Line) : home, draw, away et les sauvegarde.
# -----------------------------------------------------------------------------

import os
import json
import yaml
import requests

# Chargement des clés API
with open("config/pinnacle_keys.yaml", "r") as f:
    keys = yaml.safe_load(f)

headers = {
    "x-rapidapi-key": keys["pinnacle"]["key"],
    "x-rapidapi-host": keys["pinnacle"]["host"]
}

# Appel de l'endpoint marchés pour Soccer
url = "https://pinnacle-odds.p.rapidapi.com/kit/v1/markets"
params = {
    "sport_id": 1  # Soccer
}

response = requests.get(url, headers=headers, params=params)
data = response.json()

# Filtrer les cotes Money Line disponibles (matchs ouverts)
odds = []
for ev in data.get("events", []):
    if not ev.get("is_have_odds"): continue
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
    except:
        continue

# Sauvegarde JSON
os.makedirs("data/raw/pinnacle", exist_ok=True)
with open("data/raw/pinnacle/odds_soccer.json", "w") as f:
    json.dump(odds, f, indent=2)

print("✅ Cotes Pinnacle récupérées et sauvegardées")
