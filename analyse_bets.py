import os
import json
import pandas as pd
from glob import glob
from datetime import datetime

# Constantes
TODAY = datetime.today().strftime("%Y-%m-%d")
FIXTURES_PATHS = glob(f"data/raw/fixtures_*_{TODAY}.json")
ODDS_PATHS = glob(f"data/raw/odds_*.json")
RANKING_PATH = "data/rankings.csv"

if not FIXTURES_PATHS or not ODDS_PATHS:
    print("❌ Aucune fixture ou cote trouvée pour aujourd'hui.")
    exit(1)

# Chargement du classement
if not os.path.exists(RANKING_PATH):
    print("❌ Fichier de classement introuvable : data/rankings.csv")
    exit(1)

rankings = pd.read_csv(RANKING_PATH)
if "team" not in rankings.columns or "ranking" not in rankings.columns:
    print("❌ Fichier rankings.csv invalide. Colonnes attendues : 'team', 'ranking'")
    exit(1)

rankings.set_index("team", inplace=True)

# Chargement des cotes par fixture_id
odds_dict = {}
for path in ODDS_PATHS:
    fixture_id = int(os.path.basename(path).split("_")[1].split(".")[0])
    with open(path, "r", encoding="utf-8") as f:
        raw = json.load(f)
        for match in raw:
            if "bookmakers" not in match:
                continue
            for bookmaker in match["bookmakers"]:
                if bookmaker["name"] == "Bet365":
                    for market in bookmaker["bets"]:
                        if market["name"] == "Match Winner":
                            for val in market["values"]:
                                odds_dict.setdefault(fixture_id, {})[val["value"]] = float(val["odd"])

# Analyse des value bets
bets = []

for fixture_path in FIXTURES_PATHS:
    with open(fixture_path, "r", encoding="utf-8") as f:
        fixtures = json.load(f)

    for match in fixtures:
        fid = match["fixture"]["id"]
        home = match["teams"]["home"]["name"]
        away = match["teams"]["away"]["name"]

        if home not in rankings.index or away not in rankings.index:
            continue

        # Ex. simpliste, à remplacer par une vraie stratégie à base de différence de ranking
        expected = {"Home": 0.45, "Draw": 0.25, "Away": 0.30}

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
                    "expected_value": round(value, 3)
                })

# Sauvegarde ou non
if not bets:
    print("ℹ️ Aucun value bet détecté aujourd'hui.")
    exit(0)

bets_df = pd.DataFrame(bets).sort_values("expected_value", ascending=False)
bets_df.to_csv("data/bets_today.csv", index=False)
print(f"✅ {len(bets_df)} value bets enregistrés dans data/bets_today.csv")
