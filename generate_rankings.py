import os
import json
import pandas as pd
from glob import glob
from collections import defaultdict

# Paramètres de pondération (à adapter si tu veux)
W_GOALS_FOR = 3.0
W_GOALS_AGAINST = -2.0
W_FORM = 1.5
W_STANDINGS = 1.0  # Optionnel (non utilisé par défaut)

def extract_stats(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    team_stats = {}
    for team in data.get("response", []):
        name = team["team"]["name"]
        last_matches = team["fixtures"]["last_5"]  # peut être vide parfois
        gf = team["goals"]["for"]["total"].get("last_5", 0)
        ga = team["goals"]["against"]["total"].get("last_5", 0)

        wins = last_matches.get("wins", 0)
        draws = last_matches.get("draws", 0)
        losses = last_matches.get("loses", 0)
        total = wins + draws + losses or 1

        form_ratio = (wins + 0.5 * draws) / total

        team_stats[name] = {
            "avg_goals_for": gf / 5,
            "avg_goals_against": ga / 5,
            "form_ratio": form_ratio,
        }
    return team_stats

def generate_global_ranking():
    stats_dir = "data/raw/"
    stats_files = glob(os.path.join(stats_dir, "statistics_*.json"))

    scores = {}
    for f in stats_files:
        team_stats = extract_stats(f)
        for team, values in team_stats.items():
            score = (
                W_GOALS_FOR * values["avg_goals_for"]
                + W_GOALS_AGAINST * values["avg_goals_against"]
                + W_FORM * values["form_ratio"]
            )
            if team not in scores or score > scores[team]:
                scores[team] = round(score * 100 + 1000)  # Normalisation style ELO

    return pd.DataFrame([
        {"team_name": team, "score": score}
        for team, score in sorted(scores.items(), key=lambda x: -x[1])
    ])

if __name__ == "__main__":
    df = generate_global_ranking()
    os.makedirs("data", exist_ok=True)
    df.to_csv("data/rankings.csv", index=False)
    print(f"✅ {len(df)} équipes enregistrées dans data/rankings.csv")
