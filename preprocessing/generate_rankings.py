# preprocessing/generate_rankings.py
# ---------------------------------------------------------
# Génère un classement simple basé sur les statistiques de match (wins/games)
# ---------------------------------------------------------

import os
import json
import pandas as pd
from glob import glob

RAW_DATA_DIR = "data/raw"
OUTPUT_FILE = "data/rankings.csv"

def extract_team_stats(stats):
    home = stats.get("teams", {}).get("home", {})
    away = stats.get("teams", {}).get("away", {})

    result = {}
    for team in [home, away]:
        name = team.get("name")
        wins = team.get("statistics", {}).get("wins", {}).get("total")
        played = team.get("statistics", {}).get("played", {}).get("total")

        if name and wins is not None and played is not None:
            result[name] = {
                "games_played": played,
                "wins": wins
            }
    return result

def main():
    stats_files = glob(os.path.join(RAW_DATA_DIR, "stats_*.json"))
    if not stats_files:
        print("❌ Aucun fichier de stats trouvé.")
        return

    team_stats = {}

    for path in stats_files:
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
                for match in data.get("response", []):
                    match_stats = extract_team_stats(match)
                    for team, stats in match_stats.items():
                        if team not in team_stats:
                            team_stats[team] = {"games_played": 0, "wins": 0}
                        team_stats[team]["games_played"] += stats["games_played"]
                        team_stats[team]["wins"] += stats["wins"]
        except Exception as e:
            print(f"⚠️ Erreur lecture {path} : {e}")
            continue

    rows = []
    for team, stats in team_stats.items():
        games_played = stats.get("games_played", 0)
        wins = stats.get("wins", 0)

        if games_played == 0:
            continue  # Évite division par zéro

        win_rate = wins / games_played
        rows.append({
            "team": team,
            "games_played": games_played,
            "wins": wins,
            "win_rate": win_rate
        })

    if not rows:
        print("❌ Aucun ranking exploitable, fichier non généré.")
        return

    df_rankings = pd.DataFrame(rows).sort_values(by="win_rate", ascending=False)
    df_rankings["ranking"] = range(1, len(df_rankings) + 1)
    df_rankings.to_csv(OUTPUT_FILE, index=False)
    print("✅ Fichier rankings.csv généré avec succès.")

if __name__ == "__main__":
    main() 
