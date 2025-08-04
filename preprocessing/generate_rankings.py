# preprocessing/generate_rankings.py
import os
import json
import pandas as pd
from glob import glob

INPUT_FOLDER = "data/raw"
OUTPUT_FILE = "data/rankings.csv"

def compute_team_strength(stats):
    """Calcule un score simple basé sur les performances générales."""
    try:
        goals_for = stats["goals"]["for"]["total"]["total"] or 0
        goals_against = stats["goals"]["against"]["total"]["total"] or 1  # éviter division par 0
        form = stats.get("form", "").count("W")  # nombre de victoires récentes
        return (goals_for / goals_against) + form
    except:
        return 0

def main():
    stats_files = glob(os.path.join(INPUT_FOLDER, "stats_*.json"))
    if not stats_files:
        print("❌ Aucun fichier de stats trouvé.")
        return

    team_scores = []

    for path in stats_files:
        with open(path, "r", encoding="utf-8") as f:
            raw = json.load(f)
            for team_stats in raw.get("response", []):
                team = team_stats["team"]["name"]
                stats = team_stats["statistics"]
                score = compute_team_strength(stats)
                team_scores.append((team, score))

    if not team_scores:
        print("❌ Aucune statistique de team valide trouvée.")
        return

    df = pd.DataFrame(team_scores, columns=["team", "score"])
    df = df.groupby("team").mean().reset_index()
    df["ranking"] = df["score"].rank(ascending=False, method="min").astype(int)
    df = df.sort_values("ranking")
    df.to_csv(OUTPUT_FILE, index=False)
    print(f"✅ Fichier rankings sauvegardé dans {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
