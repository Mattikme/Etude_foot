import os
import json
import pandas as pd
from glob import glob
from datetime import datetime, timedelta

YESTERDAY = (datetime.today() - timedelta(days=1)).strftime("%Y-%m-%d")
BETS_FILE = f"data/bets_{YESTERDAY}.csv"
FIXTURES_FILE = f"data/raw/fixtures_*_{YESTERDAY}.json"

# Récupérer tous les fichiers fixtures du jour d'avant
fixtures_files = glob(FIXTURES_FILE)
if not os.path.exists(BETS_FILE):
    print(f"⚠️ Aucune donnée de paris trouvée pour {YESTERDAY}")
    exit()

bets_df = pd.read_csv(BETS_FILE)
results = []

# Lecture des résultats de chaque match joué
fixture_results = {}
for file in fixtures_files:
    with open(file, "r", encoding="utf-8") as f:
        data = json.load(f)
        for match in data.get("response", []):
            home = match["teams"]["home"]["name"]
            away = match["teams"]["away"]["name"]
            fixture_id = match["fixture"]["id"]
            goals = match["goals"]
            if goals["home"] is not None and goals["away"] is not None:
                result = "Draw"
                if goals["home"] > goals["away"]:
                    result = "Home"
                elif goals["away"] > goals["home"]:
                    result = "Away"
                fixture_results[(home, away)] = result

# Évaluation des paris
for _, row in bets_df.iterrows():
    home, away = row["match"].split(" vs ")
    actual = fixture_results.get((home, away))
    if actual:
        won = actual == row["bet_on"]
        roi = row["bookmaker_odds"] - 1 if won else -1
        results.append({
            "match": row["match"],
            "bet_on": row["bet_on"],
            "actual_result": actual,
            "bookmaker_odds": row["bookmaker_odds"],
            "won": won,
            "roi": roi
        })

results_df = pd.DataFrame(results)
if not results_df.empty:
    print("🎯 Résultats des paris d'hier :")
    print(results_df[["match", "bet_on", "actual_result", "won", "roi"]])
    print(f"🔢 ROI total : {results_df['roi'].sum():.2f}")
    results_df.to_csv(f"data/bets_results_{YESTERDAY}.csv", index=False)
else:
    print("❌ Aucun match terminé trouvé pour les paris d'hier.")
