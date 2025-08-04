
import os
import json
import pandas as pd
from glob import glob
from datetime import datetime

# Charger les fixtures et les cotes disponibles
TODAY = datetime.today().strftime("%Y-%m-%d")
fixtures_files = glob(f"data/raw/fixtures_*_{TODAY}.json")
odds_files = glob(f"data/raw/odds_*_{TODAY}.json")

if not fixtures_files or not odds_files:
    print("❌ Aucune fixture ou cote trouvée pour aujourd'hui.")
    exit(1)

# Chargement du classement
ranking_path = "data/rankings.csv"
if not os.path.exists(ranking_path):
    print("❌ Fichier de classement introuvable : data/rankings.csv")
    exit(1)

rankings = pd.read_csv(ranking_path).set_index("team")

# Chargement des cotes par fixture_id
odds_dict = {}
for path in odds_files:
    with open(path, "r", encoding="utf-8") as f:
        raw = json.load(f)
        for match in raw.get("response", []):
            fixture_id = match["fixture"]["id"]
            bookmakers = match.get("bookmakers", [])
            for bm in bookmakers:
                if bm["name"] == "Bet365":
                    for market in bm["bets"]:
                        if market["name"] == "Match Winner":
                            for val in market["values"]:
                                odds_dict.setdefault(fixture_id, {})[val["value"]] = float(val["odd"])

bets = []

for fixture_path in fixtures_files:
    with open(fixture_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        for match in data.get("response", []):
            fid = match["fixture"]["id"]
            home = match["teams"]["home"]["name"]
            away = match["teams"]["away"]["name"]
            if home not in rankings.index or away not in rankings.index:
                continue
            rank_home = rankings.loc[home]["ranking"]
            rank_away = rankings.loc[away]["ranking"]
            expected = {"Home": 0.5, "Draw": 0.2, "Away": 0.3}  # à adapter selon ta stratégie

            if fid not in odds_dict:
                continue
            for outcome in ["Home", "Draw", "Away"]:
                if outcome not in odds_dict[fid]:
                    continue
                odd = odds_dict[fid][outcome]
                fair_prob = expected[outcome]
                value = (odd * fair_prob) - 1
                if value > 0.05:
                    bets.append({
                        "match": f"{home} vs {away}",
                        "bet_on": outcome,
                        "bookmaker_odds": odd,
                        "expected_prob": fair_prob,
                        "expected_value": value
                    })

if not bets:
    print("ℹ️ Aucun value bet détecté aujourd'hui.")
    exit(0)

bets_df = pd.DataFrame(bets)
bets_df.sort_values("expected_value", ascending=False, inplace=True)
bets_df.to_csv("data/bets_today.csv", index=False)
print(f"✅ {len(bets_df)} value bets enregistrés dans data/bets_today.csv")
