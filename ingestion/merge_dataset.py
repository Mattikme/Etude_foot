# ingestion/merge_dataset.py
# -----------------------------------------------------------------------------
# Ce script fusionne les données brutes (fixtures, stats, lineups, etc.)
# en un seul DataFrame exploitable pour l'entraînement du modèle LSTM.
# Il extrait des features de base comme : résultats, stats match, absents, etc.
# -----------------------------------------------------------------------------

import os
import json
import pandas as pd
from glob import glob

LEAGUE_ID = 39
SEASON = 2022

# Chargement des matchs de base
with open(f"data/raw/fixtures_{LEAGUE_ID}_{SEASON}.json", "r") as f:
    raw_fixtures = json.load(f)["response"]

matches = []
for match in raw_fixtures:
    fixture_id = match["fixture"]["id"]
    date = match["fixture"]["date"]
    home = match["teams"]["home"]["name"]
    away = match["teams"]["away"]["name"]
    goals_home = match["goals"]["home"]
    goals_away = match["goals"]["away"]
    status = match["fixture"]["status"]["short"]
    matches.append({
        "fixture_id": fixture_id,
        "date": date,
        "home": home,
        "away": away,
        "goals_home": goals_home,
        "goals_away": goals_away,
        "status": status
    })

# Conversion en DataFrame principal
matches_df = pd.DataFrame(matches)

# Enregistrement CSV intermédiaire pour future ingestion ML
os.makedirs("data/processed", exist_ok=True)
matches_df.to_csv("data/processed/base_matches.csv", index=False)

print("✅ Base de données fusionnée : data/processed/base_matches.csv")
