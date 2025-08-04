
import os
import json
import pandas as pd
from glob import glob

# Chargement du ranking
ranking_df = pd.read_csv("data/rankings.csv")
ranking = dict(zip(ranking_df["team_name"], ranking_df["score"]))

# Params
ODDS_DIR = "data/raw/"
FIXTURES_DIR = "data/raw/"
TODAY = pd.Timestamp.today().strftime("%Y-%m-%d")

# Trouver les fichiers fixtures et odds
fixtures_files = glob(os.path.join(FIXTURES_DIR, f"fixtures_*_{TODAY}.json"))
odds_files = glob(os.path.join(ODDS_DIR, f"odds_*_{TODAY}.json"))

# Fusion des odds dans un dict {fixture_id: odds}
def load_odds():
    odds_dict = {}
    for file in odds_files:
        with open(file, "r", encoding="utf-8") as f:
            data = json.load(f)
            for match in data.get("response", []):
                fixture_id = match["fixture"]["id"]
                bookmakers = match.get("bookmakers", [])
                for bm in bookmakers:
                    if bm["name"] == "Bet365":
                        for bet in bm.get("bets", []):
                            if bet["name"] == "Match Winner":
                                odds = {odd["value"]: float(odd["odd"]) for odd in bet["values"]}
                                odds_dict[fixture_id] = odds
    return odds_dict

# Calcul de value bet simple basé sur le ranking
def compute_prediction(home, away):
    h_score = ranking.get(home, 1500)
    a_score = ranking.get(away, 1500)
    h_prob = h_score / (h_score + a_score)
    a_prob = 1 - h_prob
    draw_prob = 0.20  # estimation fixe
    return h_prob * 0.8, draw_prob, a_prob * 0.8

# Analyse principale
bets = []
odds_dict = load_odds()

for file in fixtures_files:
    with open(file, "r", encoding="utf-8") as f:
        data = json.load(f)
        for match in data.get("response", []):
            home = match["teams"]["home"]["name"]
            away = match["teams"]["away"]["name"]
            fixture_id = match["fixture"]["id"]

            pred_home, pred_draw, pred_away = compute_prediction(home, away)
            odds = odds_dict.get(fixture_id)
            if not odds:
                continue

            for side, prob in zip(["Home", "Draw", "Away"], [pred_home, pred_draw, pred_away]):
                if side in odds:
                    implied = 1 / odds[side]
                    if prob > implied:
                        bets.append({
                            "match": f"{home} vs {away}",
                            "bet_on": side,
                            "our_prob": round(prob, 2),
                            "bookmaker_odds": odds[side],
                            "expected_value": round(prob * odds[side] - 1, 2)
                        })

# Résultat
df = pd.DataFrame(bets)
if df.empty:
    print("⚠️ Aucun value bet détecté aujourd’hui.")
else:
    print("🎯 Value bets détectés :
")
    print(df.sort_values("expected_value", ascending=False))
    df.to_csv("data/bets_today.csv", index=False)
    print("\n📁 Exporté dans data/bets_today.csv")
