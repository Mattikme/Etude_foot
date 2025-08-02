# preprocessing/match_odds_mapper.py
# -----------------------------------------------------------------------------
# Ce script aligne les cotes Pinnacle avec les matchs issus d'API-Football
# en utilisant la date et les noms d'équipes. Il génère un fichier odds.csv exploitable.
# -----------------------------------------------------------------------------

import json
import pandas as pd
from difflib import SequenceMatcher

# Chargement des données de fixtures (API-Football)
fixtures = pd.read_csv("data/processed/base_matches.csv")

# Chargement des cotes Pinnacle
with open("data/raw/pinnacle/odds_soccer.json", "r") as f:
    pinnacle_odds = json.load(f)

mapped = []

# Match sur noms + date (approx)
def similar(a, b):
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

for p in pinnacle_odds:
    for _, f in fixtures.iterrows():
        if p["date"][:10] != f["date"][:10]:
            continue
        score_home = similar(p["home"], f["home"])
        score_away = similar(p["away"], f["away"])
        if score_home > 0.8 and score_away > 0.8:
            mapped.append({
                "fixture_id": f["fixture_id"],
                "date": f["date"],
                "home": f["home"],
                "away": f["away"],
                "odds_home": p["odds_home"],
                "odds_draw": p["odds_draw"],
                "odds_away": p["odds_away"]
            })
            break

# Export en CSV utilisable pour backtest
odds_df = pd.DataFrame(mapped)
odds_df.to_csv("data/odds.csv", index=False)

print("✅ Cotes mappées sauvegardées dans data/odds.csv")
