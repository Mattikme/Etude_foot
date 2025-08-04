# preprocessing/generate_rankings.py
import os
import pandas as pd
from collections import defaultdict

RAW_DIR = "data/raw"
OUTPUT_PATH = "data/rankings.csv"

def main():
    team_stats = defaultdict(lambda: {"wins": 0, "draws": 0, "losses": 0, "games": 0})

    # On balaye tous les fichiers fixtures existants
    for filename in os.listdir(RAW_DIR):
        if filename.startswith("fixtures_") and filename.endswith(".json"):
            filepath = os.path.join(RAW_DIR, filename)
            try:
                df = pd.read_json(filepath)
                for match in df:
                    fixture = match.get("fixture", {})
                    teams = match.get("teams", {})
                    goals = match.get("goals", {})

                    if not fixture or not teams or not goals:
                        continue

                    home = teams["home"]["name"]
                    away = teams["away"]["name"]
                    home_goals = goals["home"]
                    away_goals = goals["away"]

                    if home_goals is None or away_goals is None:
                        continue  # Match pas encore joué

                    team_stats[home]["games"] += 1
                    team_stats[away]["games"] += 1

                    if home_goals > away_goals:
                        team_stats[home]["wins"] += 1
                        team_stats[away]["losses"] += 1
                    elif away_goals > home_goals:
                        team_stats[away]["wins"] += 1
                        team_stats[home]["losses"] += 1
                    else:
                        team_stats[home]["draws"] += 1
                        team_stats[away]["draws"] += 1

            except Exception as e:
                print(f"❌ Erreur lecture {filename} : {e}")

    # Convertir en DataFrame
    rows = []
    for team, stats in team_stats.items():
        total = stats["games"]
        if total == 0:
            continue
        win_rate = stats["wins"] / total
        draw_rate = stats["draws"] / total
        loss_rate = stats["losses"] / total
        rows.append({
            "team": team,
            "games": total,
            "win_rate": round(win_rate, 3),
            "draw_rate": round(draw_rate, 3),
            "loss_rate": round(loss_rate, 3),
        })

    df_rankings = pd.DataFrame(rows).sort_values(by="win_rate", ascending=False)
    os.makedirs("data", exist_ok=True)
    df_rankings.to_csv(OUTPUT_PATH, index=False)
    print(f"✅ rankings.csv généré avec {len(df_rankings)} équipes.")

if __name__ == "__main__":
    main()
