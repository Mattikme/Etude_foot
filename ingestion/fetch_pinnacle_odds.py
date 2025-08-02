# ingestion/fetch_pinnacle_odds.py
# -----------------------------------------------------------------------------
# Ce script récupère les cotes Pinnacle (1X2) pré-match pour tous les matchs
# de football listés via l'endpoint markets, et les sauvegarde en JSON.
# -----------------------------------------------------------------------------

import os
import json
import yaml
import requests

# Charger la clé API et l'hôte Pinnacle depuis le fichier YAML
with open("config/pinnacle_keys.yaml", "r") as f:
    keys = yaml.safe_load(f)

headers = {
    "x-rapidapi-key": keys["pinnacle"]["key"],
    "x-rapidapi-host": keys["pinnacle"]["host"]
}

# Endpoint pour les marchés de football (soccer)
url = "https://pinnacle-odds.p.rapidapi.com/kit/v1/markets"
params = {"sport_id": 1}  # Football

try:
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    data = response.json()
except Exception as e:
    print(f"❌ Erreur lors de l'appel API Pinnacle: {e}")
    data = {}

# Extraire les cotes valides pour le marché 1X2 (Money Line)
odds = []
for ev in data.get("events", []):
    if not ev.get("is_have_odds"):
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

# Sauvegarde des données
os.makedirs("data/raw/pinnacle", exist_ok=True)
with open("data/raw/pinnacle/odds_soccer.json", "w") as f_out:
    json.dump(odds, f_out, indent=2)

print("✅ Cotes Pinnacle récupérées et sauvegardées.")
